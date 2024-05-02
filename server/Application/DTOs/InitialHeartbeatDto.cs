namespace Server.Application.DTOs
{
    public class InitialHeartbeatDtoRequest
    {
       public ulong SteamId { get; set; }
       public List<string> HardDiskSerials { get; set; }
       public string SystemUUID { get; set; }
       public string MotherboardSerialNumber { get; set; }
       public string BasicHash { get; set; }
    }

    public class InitialHeartbeatDtoResponse
    {
        public int Success { get; set; }
        public string Message { get; set; }
        public string Token { get; set; }
    }
}
