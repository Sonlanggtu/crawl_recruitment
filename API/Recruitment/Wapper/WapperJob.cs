namespace Recruitment.Wapper
{
    public class Id
    {
        public string source { get; set; }
        public string created_date_crawl_job_string { get; set; }
    }

    public class WapperJob
    {
        public Id _id { get; set; }
        public int count { get; set; }
    }
}





