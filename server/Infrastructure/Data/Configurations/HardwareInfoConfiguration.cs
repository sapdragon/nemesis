using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Server.Domain.Entities;

namespace Server.Infrastructure.Data.Configurations
{
    public class HardwareInfoConfiguration : IEntityTypeConfiguration<HardwareInfo>
    {
        public void Configure(EntityTypeBuilder<HardwareInfo> builder)
        {
            builder.Property(h => h.SystemUUID).HasMaxLength(255);
            builder.Property(h => h.MotherboardSerialNumber).HasMaxLength(255);
            builder.Property(h => h.BasicHash).HasMaxLength(255);

            builder.Property(h => h.HardDiskSerials).HasConversion(
                v => string.Join(',', v),
                v => v.Split(',', StringSplitOptions.RemoveEmptyEntries).ToList()
            );
        }
    }
}
