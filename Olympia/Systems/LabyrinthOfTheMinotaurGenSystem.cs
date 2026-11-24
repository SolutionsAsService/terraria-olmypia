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
    /// <summary>Adds LabyrinthOfTheMinotaur to world generation (site: underground) and stocks its chests by role. The layout is LabyrinthOfTheMinotaurBlueprint.</summary>
    public class LabyrinthOfTheMinotaurGenSystem : ModSystem
    {
        private static readonly int[][] ChestCells = new int[][]
        {
            new int[] { 7, 3 },
            new int[] { 62, 18 },
            new int[] { 72, 18 },
            new int[] { 72, 3 },
            new int[] { 27, 33 },
            new int[] { 27, 18 },
            new int[] { 57, 28 },
            new int[] { 52, 8 },
        };

        private static readonly string[] ChestRoles = new string[] { "great", "dead_end", "dead_end", "dead_end", "dead_end", "dead_end", "dead_end", "dead_end" };

        public override void ModifyWorldGenTasks(List<GenPass> tasks, ref double totalWeight)
        {
            int index = tasks.FindIndex(pass => pass.Name.Equals("Pyramids"));
            if (index == -1)
            {
                index = tasks.Count - 1;
            }
            tasks.Insert(index + 1, new PassLegacy("LabyrinthOfTheMinotaur", GenerateLabyrinthOfTheMinotaur));
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

        private static void GenerateLabyrinthOfTheMinotaur(GenerationProgress progress, GameConfiguration configuration)
        {
            progress.Message = "Building the Labyrinth of the Minotaur";
            int W = LabyrinthOfTheMinotaurBlueprint.Width;
            int H = LabyrinthOfTheMinotaurBlueprint.Height;
            int groundRow = LabyrinthOfTheMinotaurBlueprint.GroundRow;
            int x0 = WorldGen.genRand.Next(Main.maxTilesX / 6, Main.maxTilesX * 5 / 6 - W);
            int y0 = (int)Main.rockLayer + 40 + WorldGen.genRand.Next(0, 120);
            if (y0 + H > Main.maxTilesY - 260)
            {
                y0 = Main.maxTilesY - 260 - H;
            }
            int bestX = x0;
            int top = y0;
            for (int y = top - 1; y < top + H + 1; y++)
            {
                for (int x = bestX - 1; x < bestX + W + 1; x++)
                {
                    Main.tile[x, y].ClearEverything();
                }
            }
            Dictionary<char, int> tiles = new Dictionary<char, int>();
            tiles['L'] = ModContent.TileType<Tiles.BlackMarbleTile>();
            tiles['H'] = ModContent.TileType<Tiles.MeanderBrickTile>();
            tiles['B'] = ModContent.TileType<Tiles.OlympianMarbleTile>();
            tiles['G'] = ModContent.TileType<Tiles.BronzePlateTile>();
            for (int r = 0; r < H; r++)
            {
                progress.Set(r / (float)H);
                string row = LabyrinthOfTheMinotaurBlueprint.Decode(r);
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
                        tile.WallType = WallID.GrayBrick;
                    }
                    else
                    {
                        WorldGen.PlaceTile(x, y, tiles[ch], true, true);
                    }
                }
            }
            for (int r = 0; r < H; r++)
            {
                string row = LabyrinthOfTheMinotaurBlueprint.Decode(r);
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
                case "great":
                    if (WorldGen.genRand.Next(1) == 0) { Put(chest, ref slot, ItemID.GoldCoin, WorldGen.genRand.Next(8, 21)); }
                    if (WorldGen.genRand.Next(1) == 0) { Put(chest, ref slot, ModContent.ItemType<Items.HornOfTheLabyrinth>(), WorldGen.genRand.Next(1, 2)); }
                    if (WorldGen.genRand.Next(2) == 0) { Put(chest, ref slot, ModContent.ItemType<Items.Labrys>(), WorldGen.genRand.Next(1, 2)); }
                    if (WorldGen.genRand.Next(2) == 0) { Put(chest, ref slot, ModContent.ItemType<Items.WingedSandals>(), WorldGen.genRand.Next(1, 2)); }
                    break;
                case "dead_end":
                    if (WorldGen.genRand.Next(1) == 0) { Put(chest, ref slot, ItemID.GoldCoin, WorldGen.genRand.Next(1, 5)); }
                    if (WorldGen.genRand.Next(1) == 0) { Put(chest, ref slot, ModContent.ItemType<Items.BronzeBar>(), WorldGen.genRand.Next(3, 9)); }
                    if (WorldGen.genRand.Next(2) == 0) { Put(chest, ref slot, ModContent.ItemType<Items.AmbrosiaFlower>(), WorldGen.genRand.Next(1, 4)); }
                    if (WorldGen.genRand.Next(1) == 0) { Put(chest, ref slot, ItemID.HealingPotion, WorldGen.genRand.Next(1, 3)); }
                    break;
                }
            }
            // a three-wide shaft with a rope from the entrance up to the surface
            int sx = bestX + 2;
            int surfaceY = SurfaceY(sx + 1);
            for (int y = top + 1; y >= Math.Max(surfaceY - 2, 60); y--)
            {
                for (int dx = 0; dx < 3; dx++)
                {
                    Main.tile[sx + dx, y].ClearEverything();
                }
                WorldGen.PlaceTile(sx + 1, y, TileID.Rope, true, true);
            }
            Systems.OlympiaWorld.LabyrinthOfTheMinotaurArea = new Rectangle(bestX, top, W, H);
        }
    }
}
