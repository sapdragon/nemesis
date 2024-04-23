using Microsoft.EntityFrameworkCore;
using Server.Domain.Interfaces;
using Server.Infrastructure.Data;
using Server.Infrastructure.Repositories;
using System.Net.WebSockets;
using System.Text;

namespace Server
{
    public class Startup
    {
        public void ConfigureServices(IServiceCollection services, IConfiguration configuration)
        {
            services.AddDbContext<DatabaseContext>(options =>
            {
                options.UseSqlite("Data Source=anti-cheat.db");
            });

            services.AddScoped<IUserRepository, UserRepository>();
            services.AddScoped<IHardwareInfoRepository, HardwareInfoRepository>();
            services.AddScoped<IGameAccountRepository, GameAccountRepository>();

            services.AddSignalR();
        }


        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            app.UseRouting();
            app.UseWebSockets();

            app.UseEndpoints(endpoints =>
            {
                endpoints.MapGet("/", async context =>
                {
                    await context.Response.WriteAsync("Hello world!");
                }).RequireHost("localhost:5001");

                endpoints.MapGet("/", async context =>
                {
                    await context.Response.WriteAsync("Another message");
                }).RequireHost("localhost:5000");


            });
        }
    }

    public static class StartupExtensions
    {
        public static IServiceCollection AddCustomServices(this IServiceCollection services, IConfiguration configuration)
        {
            var startup = new Startup();
            startup.ConfigureServices(services, configuration);
            
            return services;
        }

        public static IApplicationBuilder UseCustomServices(this IApplicationBuilder app, IWebHostEnvironment env)
        {
            var startup = new Startup();
            startup.Configure(app, env);

            return app;
        }
    }
}