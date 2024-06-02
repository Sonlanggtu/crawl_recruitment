using MongoDB.Bson.Serialization.Attributes;
using MongoDB.Bson;

namespace Recruitment.Repository.Entities
{
    public class Job_Error
    {

        [BsonId]
        [BsonRepresentation(BsonType.ObjectId)]
        public string id { get; set; }

        [BsonElement("id_error")]
        public string id_error { get; set; }
        [BsonElement("source")]
        public string source { get; set; }
        [BsonElement("error_message")]
        public string error_message { get; set; }
        [BsonElement("created_date")]
        public DateTime created_date { get; set; }

        [BsonElement("created_date_string")]
        public string created_date_string { get; set; }

    }
}
