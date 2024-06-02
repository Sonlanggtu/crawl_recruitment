using Microsoft.Extensions.Configuration;
using Microsoft.OpenApi.Models;
using Recruitment.Model;
using Recruitment.Repository;
using Recruitment.Services;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.

builder.Services.AddControllers();
// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

builder.Services.Configure<DbConfiguration>(builder.Configuration.GetSection("MongoDbConnection"));

// Register Serivce and Repository
builder.Services.AddScoped<ICrawlService, CrawlService>();
builder.Services.AddScoped<ICrawlRepository, CrawlRepository>();

//Log.Logger = new LoggerConfiguration()
//           .WriteTo.Seq("http://localhost:5341")
//           .WriteTo.Console()
//           .CreateLogger();

builder.Services.AddControllers();

var app = builder.Build();

// Configure the HTTP request pipeline.
app.UseSwagger();
app.UseSwaggerUI();

app.UseHttpsRedirection();

app.UseAuthorization();

app.MapControllers();

app.Run();
