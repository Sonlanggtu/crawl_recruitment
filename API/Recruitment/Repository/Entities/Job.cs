using MongoDB.Bson.Serialization.Attributes;
using MongoDB.Bson;

namespace Recruitment.Repository.Entities
{
    public class Job
    {
        [BsonId]
        [BsonRepresentation(BsonType.ObjectId)]
        public string id { get; set; }

        [BsonElement("id_record")]
        public object id_record { get; set; }
        [BsonElement("alias")]
        public string alias { get; set; }

        [BsonElement("source")]
        public string source { get; set; }

        [BsonElement("url")]
        public string url { get; set; }
        [BsonElement("position")]
        public object position { get; set; }
        [BsonElement("created_date")]
        public object created_date { get; set; }
        [BsonElement("exp_date")]
        public object exp_date { get; set; }
        [BsonElement("company_name")]
        public string company_name { get; set; }
        [BsonElement("company_description")]
        public string company_description { get; set; }
        [BsonElement("working_address")]
        public object working_address { get; set; }
        [BsonElement("job_description")]
        public string job_description { get; set; }
        [BsonElement("job_position")]
        public object job_position { get; set; }
        [BsonElement("branch")]
        public object branch { get; set; }
        [BsonElement("skill_requirements")]
        public string skill_requirements { get; set; }
        [BsonElement("benefit")]
        public string benefit { get; set; }
        [BsonElement("contract_type")]
        public object contract_type { get; set; }
        [BsonElement("gender")]
        public string gender { get; set; }
        [BsonElement("working_area")]
        public object working_area { get; set; }
        [BsonElement("current_level")]
        public string current_level { get; set; }
        [BsonElement("desired_level")]
        public string desired_level { get; set; }
        [BsonElement("experience")]
        public object experience { get; set; }
        [BsonElement("skill")]
        public object skill { get; set; }
        [BsonElement("job_group_priority")]
        public string job_group_priority { get; set; }
        [BsonElement("salary")]
        public string salary { get; set; }
        [BsonElement("level_of_readiness")]
        public string level_of_readiness { get; set; }
        [BsonElement("number_of_vacancies")]
        public string number_of_vacancies { get; set; }
        [BsonElement("working_form")]
        public object working_form { get; set; }

        [BsonElement("created_date_crawl_job")]
        public DateTime created_date_crawl_job { get; set; }

        [BsonElement("created_date_crawl_job_string")]
        public string created_date_crawl_job_string { get; set; }
    }
}
