using Server.Domain.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using System.Numerics;

namespace Server.Infrastructure.Data.Configurations
{
    public class UserConfiguration : IEntityTypeConfiguration<User>
    {
        public void Configure(EntityTypeBuilder<User> builder)
        {
            builder.HasKey(u => u.Id);
            builder.HasMany(u => u.SteamAccounts).WithOne(s => s.User).HasForeignKey(s => s.UserId);
            builder.HasOne(u => u.hardwareInfo).WithOne(h => h.User).HasForeignKey<HardwareInfo>(h => h.UserId);
            builder.Property(u => u.IsBanned).HasDefaultValue(false);
            builder.Property(u => u.BanReason).HasMaxLength(255);
        }
    }
}
