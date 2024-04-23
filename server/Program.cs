using Server;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddCustomServices( builder.Configuration);
builder.WebHost.UseUrls("http://localhost:5000", "https://localhost:5001");

var app = builder.Build();
app.UseCustomServices(builder.Environment);
app.Run();
