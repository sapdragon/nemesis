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
            builder.Property(u => u.SteamId).IsRequired();
            builder.Property(u => u.IsBanned).HasDefaultValue(false);
            builder.Property(u => u.BanReason).HasMaxLength(255);
        }
    }
}
