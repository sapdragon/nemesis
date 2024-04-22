using Microsoft.EntityFrameworkCore;
using Server.Domain.Interfaces;
using Server.Infrastructure.Data;
using Server.Infrastructure.Repositories;

namespace Server
{
    public static class Startup
    {
        public static IServiceCollection ConfigureServices(this IServiceCollection services, IConfiguration configuration)
        {
            services.AddDbContext<DatabaseContext>(options =>
            {
                options.UseNpgsql(configuration.GetConnectionString("DefaultConnection"));
            });

            services.AddScoped<IUserRepository, UserRepository>();

            return services;
        }

    }
}
    