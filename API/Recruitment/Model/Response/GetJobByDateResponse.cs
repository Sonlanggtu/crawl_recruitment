using Recruitment.Repository.Entities;
using System.Text.Json.Serialization;

namespace Recruitment.Model.Response
{
    public class GetJobByDateResponse
    {
        public string Website { get; set; }
        public string CreatedDate { get; set; }

        [JsonIgnore]
        public DateTime CreatedDate_DateTime { get; set; }
        public int TotalRecordCrawl { get; set; } = 0;
        public bool HasError { get; set; }
        public List<Job_Error> JobErrors { get; set; } = new List<Job_Error>(); 
    }
}
