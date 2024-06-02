using FluentValidation;
using Recruitment.Model.CrawlModel;
using System.Globalization;

namespace Recruitment.Validator.Crawl
{

    public class GetJobByDateValidator : AbstractValidator<GetJobByDateRequest>
    {
        public GetJobByDateValidator()
        {

            RuleFor(x => x.From).NotEmpty().WithMessage("From is required")
                                .Must(ValidDate).WithMessage("From must to format dd/MM/yyyy");

            RuleFor(x => x.To).NotEmpty().WithMessage("To is required")
                              .Must(ValidDate).WithMessage("To must to format dd/MM/yyyy");
            //RuleFor(x => x.From).NotEqual(0).When(x => x.HasDiscount);
            //RuleFor(x => x.Address).Length(20, 250);
            //RuleFor(x => x.To).Must(ValidDate).WithMessage("To must to format dd/MM/yyyy");
        }

        private bool ValidDate(string dateString)
        {
            DateTime parsed;

            bool valid = DateTime.TryParseExact(dateString, "dd/MM/yyyy",
                                                CultureInfo.InvariantCulture,
                                                DateTimeStyles.None,
                                                out parsed);
            return valid;
        }


    }
}
