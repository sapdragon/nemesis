using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Server.Application.Interfaces;
using Server.Application.Services;
using Server.Domain.Entities;
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

            var myConfiguration = new ConfigurationBuilder()
                .SetBasePath(Directory.GetCurrentDirectory())
                .AddJsonFile("appsettings.json", optional: false, reloadOnChange: true)
                .AddEnvironmentVariables()
                .Build();

            services.AddSingleton<IConfiguration>(myConfiguration);


            services.AddScoped<IUserRepository, UserRepository>();
            services.AddScoped<IHardwareInfoRepository, HardwareInfoRepository>();
            services.AddScoped<IGameAccountRepository, GameAccountRepository>();

            services.AddTransient<IHeartbeatService, HeartbeatService>();

            services.AddControllers();
        }


        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            app.UseRouting();
            app.UseWebSockets();

            app.UseEndpoints(endpoints =>
            {
                endpoints.MapControllers()
                    .WithGroupName("websockets").RequireHost("localhost:25565");

                endpoints.MapControllers().WithGroupName("http")
            .RequireHost("localhost:25566")
 ;


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