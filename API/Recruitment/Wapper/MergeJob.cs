using Recruitment.Model.CrawlModel;
using Recruitment.Repository.Entities;

namespace Recruitment.Wapper
{
    public class MergeJob
    {
        public string CreateDateString { get; set; }
        public List<Job_Error> jobErrors { get; set; }
        public List<WapperJob> Jobs { get; set; }
    }
}
