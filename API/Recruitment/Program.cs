using Microsoft.Extensions.Configuration;
using Microsoft.OpenApi.Models;
using Recruitment.Model;
using Recruitment.Repository;
using Recruitment.Services;
using Serilog;
using System.Reflection;
using Microsoft.Extensions.Hosting;
using Serilog;
using Serilog.Events;

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


Log.Logger = new LoggerConfiguration()
    .Enrich.FromLogContext()
    .MinimumLevel.Information()
    //.WriteTo.File($"Logs/{Assembly.GetExecutingAssembly().GetName().Name}.log")
    .WriteTo.File("logs/log-.txt", rollingInterval: RollingInterval.Day)
    .WriteTo.Console()
    .CreateLogger();
builder.Logging.ClearProviders();
builder.Logging.AddSerilog();


//var builderd = Host.CreateDefaultBuilder(args)
//    .UseSerilog((context, configuration) =>
//    {
//        configuration
//            .ReadFrom.Configuration(context.Configuration)
//            .Enrich.FromLogContext()
//            .Enrich.WithMachineName()
//            .Enrich.WithThreadId()
//            .WriteTo.Console()
//            .WriteTo.File("logs/myapp.txt", rollingInterval: RollingInterval.Day);
//    })



builder.Services.AddControllers();

var app = builder.Build();

// Configure the HTTP request pipeline.
app.UseSwagger();
app.UseSwaggerUI();

//app.UseHttpsRedirection();

app.UseAuthorization();

app.MapControllers();

app.Run();
