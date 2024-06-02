using Microsoft.AspNetCore.Mvc;
using Recruitment.Model;
using Recruitment.Model.CrawlModel;
using Recruitment.Services;
using System.Net;
using Recruitment.Validator.Crawl;
using FluentValidation.Results;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc.ModelBinding;
using FluentValidation;

namespace Recruitment.Controllers
{
    [ApiController]
    [Route("api/[controller]/[action]")]
    public class CrawlController : ControllerBase
    {
        private readonly ICrawlService _crawlService;
        private readonly ILogger<CrawlController> _logger;

        public CrawlController(ICrawlService crawlService, ILogger<CrawlController> logger)
        {
            _crawlService = crawlService;
            _logger = logger;
        }

        [HttpGet]
        public async Task<IActionResult> GetJobErrorByDate([FromQuery] GetJobErrorByDateRequest request)
        {
            var validator = new GetJobErrorByDateValidator();
            ValidationResult validationResult = validator.Validate(request);
            if (!validationResult.IsValid)
            {
                object modelError = new
                {
                    message = validationResult.Errors.Select(x => x.ErrorMessage).ToArray()
                };
                return BadRequest(modelError);
            }

            var res = await _crawlService.GetJobErrorByDateAsync(request.Website, request.From, request.To);
            return Ok(res);
        }


        [HttpGet]
        public async Task<IActionResult> GetJobByDate([FromQuery] GetJobByDateRequest request)
        {
            var validator = new GetJobByDateValidator();
            ValidationResult validationResult = validator.Validate(request);
            if (!validationResult.IsValid)
            {
                object modelError = new
                {
                    message = validationResult.Errors.Select(x => x.ErrorMessage).ToArray()
                };

                return BadRequest(modelError);
            }

            var res = await _crawlService.GetJobByDateAsync(request.From, request.To);
            return Ok(res);
        }
    }
}
