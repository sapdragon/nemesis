using Server;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddCustomServices( builder.Configuration);
builder.WebHost.UseUrls("http://localhost:25565", "https://localhost:25566");

var app = builder.Build();
app.UseCustomServices(builder.Environment);
app.Run();
