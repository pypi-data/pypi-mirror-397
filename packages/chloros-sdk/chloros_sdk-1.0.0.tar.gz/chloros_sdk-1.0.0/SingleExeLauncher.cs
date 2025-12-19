using System;
using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Reflection;
using System.Threading;
using System.Windows.Forms;

namespace ChlorosSingleExe
{
    class Program
    {
        private static string tempDir;
        private static Process backendProcess;
        private static Process frontendProcess;

        [STAThread]
        static void Main(string[] args)
        {
            try
            {
                Console.WriteLine("Starting Chloros...");
                
                // Create temp directory
                tempDir = Path.Combine(Path.GetTempPath(), "Chloros_" + Guid.NewGuid().ToString("N")[..8]);
                Directory.CreateDirectory(tempDir);
                
                // Extract embedded resources
                ExtractEmbeddedApplication();
                
                // Start backend
                StartBackend();
                
                // Wait for backend to initialize
                Thread.Sleep(3000);
                
                // Start frontend
                StartFrontend();
                
                // Wait for processes to exit
                WaitForProcesses();
                
                // Cleanup
                Cleanup();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error starting Chloros: {ex.Message}", "Chloros Error", 
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private static void ExtractEmbeddedApplication()
        {
            Console.WriteLine("Extracting application files...");
            
            // Get embedded zip resource
            var assembly = Assembly.GetExecutingAssembly();
            using var stream = assembly.GetManifestResourceStream("ChlorosSingleExe.chloros_app.zip");
            
            if (stream == null)
            {
                throw new Exception("Embedded application not found!");
            }
            
            // Extract to temp directory
            using var archive = new ZipArchive(stream, ZipArchiveMode.Read);
            archive.ExtractToDirectory(tempDir);
            
            Console.WriteLine($"Extracted to: {tempDir}");
        }

        private static void StartBackend()
        {
            Console.WriteLine("Starting Python backend...");
            
            var pythonExe = Path.Combine(tempDir, "python", "python.exe");
            var backendScript = Path.Combine(tempDir, "resources", "app", "backend_server.py");
            
            if (!File.Exists(pythonExe))
            {
                throw new Exception($"Python executable not found: {pythonExe}");
            }
            
            if (!File.Exists(backendScript))
            {
                throw new Exception($"Backend script not found: {backendScript}");
            }
            
            var startInfo = new ProcessStartInfo
            {
                FileName = pythonExe,
                Arguments = $"\"{backendScript}\"",
                WorkingDirectory = tempDir,
                UseShellExecute = false,
                CreateNoWindow = true,
                RedirectStandardOutput = false,
                RedirectStandardError = false
            };
            
            // Set environment variables
            startInfo.EnvironmentVariables["PYTHONPATH"] = Path.Combine(tempDir, "resources", "app");
            startInfo.EnvironmentVariables["PATH"] = Path.Combine(tempDir, "python") + ";" + 
                Environment.GetEnvironmentVariable("PATH");
            
            backendProcess = Process.Start(startInfo);
            Console.WriteLine($"Backend started (PID: {backendProcess.Id})");
        }

        private static void StartFrontend()
        {
            Console.WriteLine("Starting Electron frontend...");
            
            var electronExe = Path.Combine(tempDir, "Chloros.exe");
            
            if (!File.Exists(electronExe))
            {
                throw new Exception($"Electron executable not found: {electronExe}");
            }
            
            var startInfo = new ProcessStartInfo
            {
                FileName = electronExe,
                WorkingDirectory = tempDir,
                UseShellExecute = false,
                CreateNoWindow = false
            };
            
            frontendProcess = Process.Start(startInfo);
            Console.WriteLine($"Frontend started (PID: {frontendProcess.Id})");
        }

        private static void WaitForProcesses()
        {
            Console.WriteLine("Chloros is running. Close the application window to exit.");
            
            // Wait for frontend to exit
            if (frontendProcess != null && !frontendProcess.HasExited)
            {
                frontendProcess.WaitForExit();
            }
            
            // Kill backend if still running
            if (backendProcess != null && !backendProcess.HasExited)
            {
                try
                {
                    backendProcess.Kill();
                    backendProcess.WaitForExit(5000);
                }
                catch { }
            }
        }

        private static void Cleanup()
        {
            Console.WriteLine("Cleaning up temporary files...");
            
            try
            {
                if (Directory.Exists(tempDir))
                {
                    // Give processes time to fully exit
                    Thread.Sleep(1000);
                    
                    // Force cleanup
                    Directory.Delete(tempDir, true);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Warning: Could not clean up temp directory: {ex.Message}");
            }
        }
    }
}
