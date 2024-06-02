using Recruitment.Model;
using Recruitment.Model.Response;
using Recruitment.Repository.Entities;
using System.Runtime.CompilerServices;

namespace Recruitment.Services
{
    public interface ICrawlService
    {
        Task<List<GetJobByDateResponse>> GetJobByDateAsync(string from, string to);
        Task<List<JobErrorResponse>> GetJobErrorByDateAsync(string website, string from, string to);
    }
}
