using Microsoft.EntityFrameworkCore;
using Server.Domain.Entities;
using Server.Domain.Interfaces;
using Server.Infrastructure.Data;

namespace Server.Infrastructure.Repositories
{
    public class HardwareInfoRepository : IHardwareInfoRepository
    {
        private readonly DatabaseContext _context;

        public HardwareInfoRepository(DatabaseContext context)
        {
            _context = context;
        }

        public async Task AddHardwareInfoAsync(HardwareInfo hardwareInfo)
        {
            await _context.HardwareInfos.AddAsync(hardwareInfo);
            await _context.SaveChangesAsync();
        }

        public async Task DeleteHardwareInfoAsync(HardwareInfo hardwareInfo)
        {
            _context.HardwareInfos.Remove(hardwareInfo);
            await _context.SaveChangesAsync();
        }

        public async Task<IEnumerable<HardwareInfo>> GetAllHardwareInfosAsync()
        {
            return await _context.HardwareInfos.ToListAsync();
        }

        public async Task<HardwareInfo> GetHardwareInfoByIdAsync(int id)
        {
            return await _context.HardwareInfos.FindAsync(id);
        }

        public async Task<HardwareInfo> GetHardwareInfoByUserIdAsync(int userId)
        {
            return await _context.HardwareInfos.FirstAsync(hardwareInfo => hardwareInfo.UserId == userId);
        }

        public async Task UpdateHardwareInfoAsync(HardwareInfo hardwareInfo)
        {
            _context.Entry(hardwareInfo).State = EntityState.Modified;
            await _context.SaveChangesAsync();
        }
    }
}
