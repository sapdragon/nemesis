using Server;

var builder = WebApplication.CreateBuilder(args);

builder.Services.ConfigureServices( builder.Configuration);

var app = builder.Build();

app.MapGet("/", () => "Hello World!");

app.Run();
