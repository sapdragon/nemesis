
namespace Server.Domain.Entities
{
    public class HardwareInfo
    {
        public int Id { get; set; }

        public int UserId { get; set; }
        public User User { get; set; }
            
        public List<string> HardDiskSerials { get; set; }
        public string SystemUUID { get; set; }
        public string MotherboardSerialNumber { get; set; }
        public string BasicHash { get; set; }

    }
}
