// final assessment from Introduction to C#

using Assessment;
using System.Net.Http;
using System.Threading.Tasks;


class Program
{
    static readonly HttpClient client = new HttpClient();

    public static async Task Main()
    {
        Words w = new Words();
        var directories = w.GetWordList();
        string host = "http://10.129.205.211/";
        foreach (string d in directories)
        {
            Console.WriteLine("Doing something else (counting):" + )
            await Requesting(host, d, "flag.txt");
        }  

        Console.WriteLine("[+] Done!");
    }

    static async Task Requesting(string host, string directory, string file)
    {
        try
        {
            Console.WriteLine("testing: " + directory);
            HttpResponseMessage response = await client.GetAsync(host + directory + "/" + file);
            int result = (int)response.StatusCode;
            if (result == 200) {
                string responseBody = await response.Content.ReadAsStringAsync();
                Console.WriteLine("Flag Found:" + host + directory + "/" + file);
                Console.Write(responseBody);
                Console.WriteLine("");
            } 
            
        } catch(HttpRequestException e) {
            Console.WriteLine("Exception Caught!");
            Console.WriteLine($"Message: {e.Message}");
        }
    }

}

