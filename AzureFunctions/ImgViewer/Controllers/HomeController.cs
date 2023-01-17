using Azure.Storage.Blobs;
using Azure.Storage.Blobs.Models;
using ImgViewer.Models;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using System.Collections.Generic;
using System.Diagnostics;

namespace ImgViewer.Controllers
{
    public class HomeController : Controller
    {

        const string blobContainerName = "fiberdefects";
        const string connectionstring = @"DefaultEndpointsProtocol=https;AccountName=camtagstoreaiem;AccountKey=TwURR9XUNY+jsvTvMzGdjUxb+x8q+MCSLiVxNwGBdg5vjwkBEP6q1DWUI+SId91AxHxJKIzOLjBq+ASt2YALow==;EndpointSuffix=core.windows.net";
        static BlobContainerClient blobContainer;

        private readonly ILogger<HomeController> _logger;

        public HomeController(ILogger<HomeController> logger)
        {
            _logger = logger;
        }
        /// <summary> 
        /// Task<ActionResult> Index() 
        /// Documentation References:  
        /// - What is a Storage Account: http://azure.microsoft.com/en-us/documentation/articles/storage-whatis-account/ 
        /// - Create a Storage Account: https://azure.microsoft.com/en-us/documentation/articles/storage-dotnet-how-to-use-blobs/#create-an-azure-storage-account
        /// - Create a Storage Container: https://azure.microsoft.com/en-us/documentation/articles/storage-dotnet-how-to-use-blobs/#create-a-container
        /// - List all Blobs in a Storage Container: https://azure.microsoft.com/en-us/documentation/articles/storage-dotnet-how-to-use-blobs/#list-the-blobs-in-a-container
        /// </summary> 
        public async Task<ActionResult> IndexOld()
        {

            try
            {
                // Retrieve storage account information from connection string
                // How to create a storage connection string - http://msdn.microsoft.com/en-us/library/azure/ee758697.aspx
                BlobServiceClient blobServiceClient = new BlobServiceClient(connectionstring);

                blobContainer = blobServiceClient.GetBlobContainerClient(blobContainerName);
                await blobContainer.CreateIfNotExistsAsync(PublicAccessType.Blob);

                // To view the uploaded blob in a browser, you have two options. The first option is to use a Shared Access Signature (SAS) token to delegate  
                // access to the resource. See the documentation links at the top for more information on SAS. The second approach is to set permissions  
                // to allow public access to blobs in this container. Comment the line below to not use this approach and to use SAS. Then you can view the image  
                // using: https://[InsertYourStorageAccountNameHere].blob.core.windows.net/webappstoragedotnet-imagecontainer/FileName 

                // Gets all Block Blobs in the blobContainerName and passes them to the view
                List<Uri> allBlobs = new List<Uri>();
                foreach (BlobItem blob in blobContainer.GetBlobs())
                {
                    if (blob.Properties.BlobType == BlobType.Block)
                        if (blob.Name.Contains("0712"))
                        {
                            allBlobs.Add(blobContainer.GetBlobClient(blob.Name).Uri);
                        }
                }

                return View(allBlobs);
            }
            catch (Exception ex)
            {
                ViewData["message"] = ex.Message;
                ViewData["trace"] = ex.StackTrace;
                return View("Error");
            }
        }
        public async Task<IActionResult> Index(string searchString = "",string numberTotake="1")
        {
            try
            {
                var number = Convert.ToInt32((string)numberTotake);
                List<Uri> allBlobs = new List<Uri>();
                if (!string.IsNullOrEmpty(searchString))
                {
                    // Retrieve storage account information from connection string
                    // How to create a storage connection string - http://msdn.microsoft.com/en-us/library/azure/ee758697.aspx
                    BlobServiceClient blobServiceClient = new BlobServiceClient(connectionstring);

                    blobContainer = blobServiceClient.GetBlobContainerClient(blobContainerName);
                    await blobContainer.CreateIfNotExistsAsync(PublicAccessType.Blob);

                    // To view the uploaded blob in a browser, you have two options. The first option is to use a Shared Access Signature (SAS) token to delegate  
                    // access to the resource. See the documentation links at the top for more information on SAS. The second approach is to set permissions  
                    // to allow public access to blobs in this container. Comment the line below to not use this approach and to use SAS. Then you can view the image  
                    // using: https://[InsertYourStorageAccountNameHere].blob.core.windows.net/webappstoragedotnet-imagecontainer/FileName 

                    // Gets all Block Blobs in the blobContainerName and passes them to the view

                    foreach (BlobItem blob in blobContainer.GetBlobs(prefix:searchString).Take<BlobItem>(number))
                    {
                        if (blob.Properties.BlobType == BlobType.Block)
                            if (blob.Name.Contains(searchString))
                            {
                              allBlobs.Add(blobContainer.GetBlobClient(blob.Name).Uri);
                            }
                    }

                }
                return View(allBlobs);
            }
            catch (Exception ex)
            {
                ViewData["message"] = ex.Message;
                ViewData["trace"] = ex.StackTrace;
                return View("Error");
            } 


        }
    
        public IActionResult Privacy()
        {
            return View();
        }

        [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
        public IActionResult Error()
        {
            return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
        }
        /// <summary> 
        /// Task<ActionResult> DeleteImage(string name) 
        /// Documentation References:  
        /// - Delete Blobs: https://azure.microsoft.com/en-us/documentation/articles/storage-dotnet-how-to-use-blobs/#delete-blobs
        /// </summary> 
        [HttpPost]
        public async Task<ActionResult> DeleteImage(string name)
        {
            try
            {
                Uri uri = new Uri(name);
                string filename = Path.GetFileName(uri.LocalPath);

                var blob = blobContainer.GetBlobClient(filename);
                await blob.DeleteIfExistsAsync();

                return RedirectToAction("Index");
            }
            catch (Exception ex)
            {
                ViewData["message"] = ex.Message;
                ViewData["trace"] = ex.StackTrace;
                return View("Error");
            }
        }

        /// <summary> 
        /// Task<ActionResult> DeleteAll(string name) 
        /// Documentation References:  
        /// - Delete Blobs: https://azure.microsoft.com/en-us/documentation/articles/storage-dotnet-how-to-use-blobs/#delete-blobs
        /// </summary> 
        [HttpPost]
        public async Task<ActionResult> DeleteAll()
        {
            try
            {
                foreach (var blob in blobContainer.GetBlobs())
                {
                    if (blob.Properties.BlobType == BlobType.Block)
                    {
                        await blobContainer.DeleteBlobIfExistsAsync(blob.Name);
                    }
                }

                return RedirectToAction("Index");
            }
            catch (Exception ex)
            {
                ViewData["message"] = ex.Message;
                ViewData["trace"] = ex.StackTrace;
                return View("Error");
            }
        }

        /// <summary> 
        /// string GetRandomBlobName(string filename): Generates a unique random file name to be uploaded  
        /// </summary> 
        private string GetRandomBlobName(string filename)
        {
            string ext = Path.GetExtension(filename);
            return string.Format("{0:10}_{1}{2}", DateTime.Now.Ticks, Guid.NewGuid(), ext);
        }

    }
}