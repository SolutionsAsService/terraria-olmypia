using System;
using System.Collections.Generic;
using Microsoft.Xna.Framework;
using Terraria;
using Terraria.GameContent.Generation;
using Terraria.ID;
using Terraria.IO;
using Terraria.ModLoader;
using Terraria.WorldBuilding;

namespace Olympia.Systems
{
    /// <summary>Adds TempleOfOlympus to world generation (site: surface) and stocks its chests by role. The layout is TempleOfOlympusBlueprint.</summary>
    public class TempleOfOlympusGenSystem : ModSystem
    {
        private static readonly int[][] ChestCells = new int[][]
        {
            new int[] { 26, 25 },
            new int[] { 38, 25 },
            new int[] { 20, 39 },
            new int[] { 29, 39 },
            new int[] { 38, 39 },
        };

        private static readonly string[] ChestRoles = new string[] { "cella", "cella", "crypt", "crypt", "crypt" };

        public override void ModifyWorldGenTasks(List<GenPass> tasks, ref double totalWeight)
        {
            int index = tasks.FindIndex(pass => pass.Name.Equals("Pyramids"));
            if (index == -1)
            {
                index = tasks.Count - 1;
            }
            tasks.Insert(index + 1, new PassLegacy("TempleOfOlympus", GenerateTempleOfOlympus));
        }

        private static int SurfaceY(int x)
        {
            for (int y = 60; y < (int)Main.worldSurface; y++)
            {
                Tile tile = Main.tile[x, y];
                if (tile.HasTile && Main.tileSolid[tile.TileType])
                {
                    return y;
                }
            }
            return -1;
        }

        private static bool IsSand(int type)
        {
            return type == TileID.Sand || type == TileID.HardenedSand || type == TileID.Sandstone;
        }

        private static void Put(Chest chest, ref int slot, int type, int stack)
        {
            if (slot < 40)
            {
                chest.item[slot].SetDefaults(type);
                chest.item[slot].stack = stack;
                slot++;
            }
        }

        private static void GenerateTempleOfOlympus(GenerationProgress progress, GameConfiguration configuration)
        {
            progress.Message = "Building the Temple of Olympus";
            int W = TempleOfOlympusBlueprint.Width;
            int H = TempleOfOlympusBlueprint.Height;
            int groundRow = TempleOfOlympusBlueprint.GroundRow;
            int bestX = -1;
            double bestScore = -1000.0;
            for (int attempt = 0; attempt < 400; attempt++)
            {
                int x0 = WorldGen.genRand.Next(Main.maxTilesX / 8, Main.maxTilesX * 7 / 8 - W);
                int sand = 0;
                int ground = 0;
                int count = 0;
                int minY = int.MaxValue;
                int maxY = 0;
                for (int x = x0; x < x0 + W; x += 3)
                {
                    int y = SurfaceY(x);
                    if (y < 0)
                    {
                        continue;
                    }
                    count++;
                    minY = Math.Min(minY, y);
                    maxY = Math.Max(maxY, y);
                    int t = Main.tile[x, y].TileType;
                    if (IsSand(t))
                    {
                        sand++;
                    }
                    else if (t == TileID.Grass || t == TileID.Dirt || t == TileID.Stone)
                    {
                        ground++;
                    }
                }
                if (count == 0)
                {
                    continue;
                }
                double score = ground / (double)count * 100.0 - (maxY - minY) * 3.0 - sand * 4.0;
                if (score > bestScore)
                {
                    bestScore = score;
                    bestX = x0;
                }
            }
            if (bestX < 0)
            {
                return;
            }
            List<int> ys = new List<int>();
            for (int x = bestX; x < bestX + W; x += 2)
            {
                int y = SurfaceY(x);
                if (y > 0)
                {
                    ys.Add(y);
                }
            }
            ys.Sort();
            int groundLine = ys[ys.Count / 2];
            int top = groundLine - groundRow;
            for (int x = bestX; x < bestX + W; x++)
            {
                for (int y = top - 2; y < groundLine; y++)
                {
                    Main.tile[x, y].ClearEverything();
                }
                for (int y = groundLine; y < groundLine + 3; y++)
                {
                    WorldGen.PlaceTile(x, y, TileID.Sandstone, true, true);
                }
            }
            Dictionary<char, int> tiles = new Dictionary<char, int>();
            tiles['B'] = ModContent.TileType<Tiles.OlympianMarbleTile>();
            tiles['H'] = ModContent.TileType<Tiles.MeanderBrickTile>();
            tiles['G'] = ModContent.TileType<Tiles.BronzePlateTile>();
            tiles['L'] = ModContent.TileType<Tiles.BlackMarbleTile>();
            for (int r = 0; r < H; r++)
            {
                progress.Set(r / (float)H);
                string row = TempleOfOlympusBlueprint.Decode(r);
                for (int c = 0; c < W; c++)
                {
                    char ch = row[c];
                    int x = bestX + c;
                    int y = top + r;
                    if (ch == ' ')
                    {
                        continue;
                    }
                    Tile tile = Main.tile[x, y];
                    tile.ClearEverything();
                    if (ch == '.' || ch == 'c' || ch == 'C' || ch == 'T' || ch == 'p' || ch == 'K' || ch == 'R')
                    {
                        tile.WallType = WallID.GrayBrick;
                    }
                    else if (ch == 'w')
                    {
                        tile.WallType = WallID.SandstoneBrick;
                    }
                    else
                    {
                        WorldGen.PlaceTile(x, y, tiles[ch], true, true);
                    }
                }
            }
            for (int r = 0; r < H; r++)
            {
                string row = TempleOfOlympusBlueprint.Decode(r);
                for (int c = 0; c < W; c++)
                {
                    int x = bestX + c;
                    int y = top + r;
                    switch (row[c])
                    {
                        case 'p':
                            WorldGen.PlaceTile(x, y, TileID.Platforms, true, true, -1, 0);
                            break;
                        case 'K':
                            WorldGen.PlaceTile(x, y, TileID.Spikes, true, true);
                            break;
                        case 'T':
                            WorldGen.PlaceTile(x, y, TileID.Torches, true, false, -1, 0);
                            break;
                    }
                }
            }
            for (int i = 0; i < ChestCells.Length; i++)
            {
                int cx = bestX + ChestCells[i][0];
                int cy = top + ChestCells[i][1];
                int index = WorldGen.PlaceChest(cx, cy, (ushort)TileID.Containers, false, 1);
                if (index < 0)
                {
                    continue;
                }
                Chest chest = Main.chest[index];
                int slot = 0;
                switch (ChestRoles[i])
                {
                case "cella":
                    if (WorldGen.genRand.Next(1) == 0) { Put(chest, ref slot, ItemID.GoldCoin, WorldGen.genRand.Next(2, 7)); }
                    if (WorldGen.genRand.Next(1) == 0) { Put(chest, ref slot, ModContent.ItemType<Items.BronzeBar>(), WorldGen.genRand.Next(4, 10)); }
                    if (WorldGen.genRand.Next(2) == 0) { Put(chest, ref slot, ModContent.ItemType<Items.Ambrosia>(), WorldGen.genRand.Next(1, 3)); }
                    if (WorldGen.genRand.Next(3) == 0) { Put(chest, ref slot, ModContent.ItemType<Items.LaurelWreath>(), WorldGen.genRand.Next(1, 2)); }
                    break;
                case "crypt":
                    if (WorldGen.genRand.Next(1) == 0) { Put(chest, ref slot, ItemID.GoldCoin, WorldGen.genRand.Next(5, 13)); }
                    if (WorldGen.genRand.Next(5) == 0) { Put(chest, ref slot, ModContent.ItemType<Items.BowOfArtemis>(), WorldGen.genRand.Next(1, 2)); }
                    if (WorldGen.genRand.Next(3) == 0) { Put(chest, ref slot, ModContent.ItemType<Items.WingedSandals>(), WorldGen.genRand.Next(1, 2)); }
                    if (WorldGen.genRand.Next(2) == 0) { Put(chest, ref slot, ModContent.ItemType<Items.HornOfTheLabyrinth>(), WorldGen.genRand.Next(1, 2)); }
                    if (WorldGen.genRand.Next(1) == 0) { Put(chest, ref slot, ModContent.ItemType<Items.AmbrosiaFlower>(), WorldGen.genRand.Next(2, 5)); }
                    break;
                }
            }
            Systems.OlympiaWorld.TempleOfOlympusArea = new Rectangle(bestX, top, W, H);
        }
    }
}
