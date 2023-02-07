// See https://aka.ms/new-console-template for more information
using Azure.Storage.Blobs;
using Azure.Storage.Blobs.Models;
using System.Collections.Generic;
using System.Diagnostics;
using System.Net.Http;


const string blobContainerName = "fiberdefectstest";
const string connectionstring = @"DefaultEndpointsProtocol=https;AccountName=camtagstoreaiem;AccountKey=TwURR9XUNY+jsvTvMzGdjUxb+x8q+MCSLiVxNwGBdg5vjwkBEP6q1DWUI+SId91AxHxJKIzOLjBq+ASt2YALow==;EndpointSuffix=core.windows.net";

try
{
    // Retrieve storage account information from connection string
    // How to create a storage connection string - http://msdn.microsoft.com/en-us/library/azure/ee758697.aspx
    BlobServiceClient blobServiceClient = new BlobServiceClient(connectionstring);

    BlobContainerClient blobContainer = blobServiceClient.GetBlobContainerClient(blobContainerName);
    await blobContainer.CreateIfNotExistsAsync(PublicAccessType.Blob);
    string searchString = "262";
    int number = 50000;

    // To view the uploaded blob in a browser, you have two options. The first option is to use a Shared Access Signature (SAS) token to delegate  
    // access to the resource. See the documentation links at the top for more information on SAS. The second approach is to set permissions  
    // to allow public access to blobs in this container. Comment the line below to not use this approach and to use SAS. Then you can view the image  
    // using: https://[InsertYourStorageAccountNameHere].blob.core.windows.net/webappstoragedotnet-imagecontainer/FileName 

    // Gets all Block Blobs in the blobContainerName and passes them to the view
    foreach (BlobItem blob in blobContainer.GetBlobs(prefix: searchString).Take<BlobItem>(number))
    { 
        //if(blob.Properties.CreatedOn>DateTimeOffset.Parse("15-01-2023 10:10:00 +00:00"))
        //{
        if (blob.Name.Contains("BL4")) { 
            Console.WriteLine(blob.Properties.CreatedOn.ToString());
            Console.WriteLine(blob.Name);
        //}
        //if (blob.Name.ToLower().Contains(""))
        //{
            await DownloadToStream(blobContainer.GetBlobClient(blob.Name), blob.Name);
        }
    }
}
catch (Exception ex)
{
}
async Task DownloadToStream(BlobClient blobClient, string localFilePath)
{
    try
    {
        FileStream fileStream = File.OpenWrite(localFilePath);
        await blobClient.DownloadToAsync(fileStream);
        fileStream.Close();
    }
    catch (DirectoryNotFoundException ex)
    {
        // Let the user know that the directory does not exist
        Console.WriteLine($"Directory not found: {ex.Message}");
    }
}