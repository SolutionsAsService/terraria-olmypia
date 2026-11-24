namespace Olympia.Systems
{
    /// <summary>The TempleOfOlympus blueprint, drawn one character per tile and run-length encoded (generated from content/structures.json by shadw-mod; do not edit).
    /// 65 wide, 43 tall, the ground at row 30.</summary>
    public static class TempleOfOlympusBlueprint
    {
        public const int Width = 65;
        public const int Height = 43;
        public const int GroundRow = 30;

        public static readonly string[] Rows = new string[]
        {
            " 27B3L5B3 27",
            " 24B3L11B3 24",
            " 21B3L17B3 21",
            " 18B3L23B3 18",
            " 15B3L29B3 15",
            " 12B3L35B3 12",
            " 9B3L41B3 9",
            " 6B3L47B3 6",
            " 3B59 3",
            " 3B59 3",
            " 4H57 4",
            " 4H57 4",
            " 3B59 3",
            " 5.1H2.4H2.4H1B2.23B2.2H2.4H2.4 5",
            " 5.1w2.4w2.4w1B2.23B2.2w2.4w2.4 5",
            " 5.1w2.4w2.4w1B2.23B2.2w2.4w2.4 5",
            " 5.1w2.4w2.4w1B2.23B2.2w2.4w2.4 5",
            " 5.1w2.4w2.4w1B2.23B2.2w2.4w2.4 5",
            " 5.1w2.4w2.4w1B2.23B2.2w2.4w2.4 5",
            " 5.1w2.4w2.4w1B2.23B2.2w2.4w2.4 5",
            " 5.1w2.4w2.4w1B2.23B2.2w2.4w2.4 5",
            " 5.1w2.4w2.4w1B2.3T1.15T1.3B2.2w2.4w2.4 5",
            " 5.1w2.4w2.4w1.29w2.4w2.4 5",
            " 5.1w2.4w2.4w1.12G3.14w2.4w2.4 5",
            " 5.1w2.4w2.4w1.11G5.13w2.4w2.4 5",
            " 5.1w2.4w2.4w1.7C1c1.2G5.3C1c1.8w2.4w2.4 5",
            " 5.1w2.4w2.4w1.7c2.2G5.3c2.8w2.4w2.4 5",
            " 4B19.3B35 4",
            " 2B21.3B37 2",
            "B23.3B39",
            "B23.3B39",
            "B23.3B39",
            "B23p3B39",
            " 23.3 39",
            " 23.3 39",
            " 18.29 18",
            " 18.2T1.5T1.5T1.5T1.5T1.2 18",
            " 18.29 18",
            " 18.29 18",
            " 18.2C1c1.7C1c1.7C1c1.7 18",
            " 18.2c2.7c2.7c2.7 18",
            " 17B31 17",
            " 17B31 17"
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
