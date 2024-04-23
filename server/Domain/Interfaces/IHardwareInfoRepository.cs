using Server.Domain.Entities;

namespace Server.Domain.Interfaces
{
    public interface IHardwareInfoRepository
    {
        Task<HardwareInfo> GetHardwareInfoByIdAsync(int id);
        Task<HardwareInfo> GetHardwareInfoByUserIdAsync(int userId);

        Task<IEnumerable<HardwareInfo>> GetAllHardwareInfosAsync();

        Task AddHardwareInfoAsync(HardwareInfo hardwareInfo);
        Task UpdateHardwareInfoAsync(HardwareInfo hardwareInfo);
        Task DeleteHardwareInfoAsync(HardwareInfo hardwareInfo);
    }
}