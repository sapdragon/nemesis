using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Server.Domain.Entities;

namespace Server.Infrastructure.Data.Configurations
{
    public class GameAccountConfiguration : IEntityTypeConfiguration<SteamAccount>
    {
        public void Configure(EntityTypeBuilder<SteamAccount> builder)
        {
            builder.HasKey(s => s.Id);
            builder.Property(s => s.SteamId).IsRequired();
            builder.Property(s => s.LastActive).HasDefaultValueSql("GETDATE()");

            builder.HasOne(s => s.User).WithMany(u => u.SteamAccounts).HasForeignKey(s => s.UserId);
        }
    }
}
