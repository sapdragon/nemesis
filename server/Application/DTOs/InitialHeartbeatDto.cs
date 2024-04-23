namespace Server.Application.DTOs
{
    public class InitialHeartbeatDto
    {
       public ulong SteamId { get; set; }
       public List<string> HardDiskSerials { get; set; }
       public string SystemUUID { get; set; }
       public string MotherboardSerialNumber { get; set; }
       public string BasicHash { get; set; }
    }
}
