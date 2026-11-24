namespace Olympia.Systems
{
    /// <summary>The LabyrinthOfTheMinotaur blueprint, drawn one character per tile and run-length encoded (generated from content/structures.json by shadw-mod; do not edit).
    /// 76 wide, 36 tall, the ground at row 0.</summary>
    public static class LabyrinthOfTheMinotaurBlueprint
    {
        public const int Width = 76;
        public const int Height = 36;
        public const int GroundRow = 0;

        public static readonly string[] Rows = new string[]
        {
            "L2.2L72",
            "L1.4L1.7T1.16L1.27T1.11L1.4L1",
            "L1.4L1.24L1.39L1.4L1",
            "L1.4L1.1C1c1.21L1.39L1.1C1c1.1L1",
            "L1.4L1.1c2.21L1.6K2.23K2.6L1.1c2.1L1",
            "L1p4L6p4L11p4L1p4L16p4L1p4L6p4L1p4L1",
            "L1.4L1.9L1.7T1.6L1.9L1.2T1.4T1.1L1.4L1.9L1.9L1",
            "L1.4L1.9L1.14L1.9L1.9L1.4L1.9L1.9L1",
            "L1.4L1.9L1.14L1.9L1.9L1.1C1c1.1L1.9L1.9L1",
            "L1.4L1.9L1.14L1.9L1.9L1.1c2.1L1.6K2.1L1.9L1",
            "L1p4L1p4L6p4L21p4L1p4L11p4L6p4L1",
            "L1.4L1.9L1.2T1.4T1.21L1.4L1.14L1.9L1",
            "L1.4L1.9L1.29L1.4L1.14L1.9L1",
            "L1.4L1.9L1.29L1.4L1.14L1.9L1",
            "L1.4L1.1K2.6L1.29L1.4L1.6K2.6L1.9L1",
            "L1p4L6p4L16.14L1p4L1p4L11p4L6",
            "L1.14L1.2T1.11L1.19L1.9L1.9L1.4L1",
            "L1.14L1.14L1.19L1.9L1.9L1.4L1",
            "L1.14L1.11C1c1.1L1.19L1.9L1.1C1c1.6L1.1C1c1.1L1",
            "L1.14L1.11c2.1L1.19L1.9L1.1c2.6L1.1c2.1L1",
            "L16p4L1p4L6.14L6p4L1p4L6p4L1p4L1",
            "L1.14L1.4L1.12L1.4L1.16L1.9L1.9L1",
            "L1.14L1.4L1.12L1.4L1.16L1.9L1.9L1",
            "L1.14L1.4L1.12L1.4L1.16L1.9L1.9L1",
            "L1.6K2.6L1.4L1.12L1.4L1.13K2.1L1.9L1.6K2.1L1",
            "L11p4L1p4L16p4L1p4L11p4L1p4L11",
            "L1.7T1.6L1.4L1.12T1.1L1.9L1.2T1.6L1.4L1.12T1.1L1",
            "L1.14L1.4L1.14L1.9L1.9L1.4L1.14L1",
            "L1.14L1.4L1.14L1.9L1.9L1.1C1c1.1L1.14L1",
            "L1.14L1.4L1.14L1.9L1.9L1.1c2.1L1.14L1",
            "L1p4L11p4L1p4L6p4L11p4L1p4L16p4L1",
            "L1.24L1.12T1.4T1.6L1.24L1",
            "L1.24L1.24L1.24L1",
            "L1.24L1.1C1c1.21L1.24L1",
            "L1.24L1.1c2.21L1.24L1",
            "H76"
        };

        /// <summary>Row r as one character per tile.</summary>
        public static string Decode(int r)
        {
            string s = Rows[r];
            var sb = new System.Text.StringBuilder();
            int i = 0;
            while (i < s.Length)
            {
                char c = s[i++];
                int n = 0;
                while (i < s.Length && char.IsDigit(s[i]))
                {
                    n = n * 10 + (s[i++] - '0');
                }
                sb.Append(c, n);
            }
            return sb.ToString();
        }
    }
}
