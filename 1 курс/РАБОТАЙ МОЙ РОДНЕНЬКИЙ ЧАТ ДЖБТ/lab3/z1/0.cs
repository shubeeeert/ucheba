namespace B
{
    public class G
    {
        public int[,] R(int c, int k)
        {
            var m = new int[c, k]; var r = new System.Random(); var d = new System.Collections.Generic.Stack<(int, int)>(); for (int i = 0; i < c; i++) for (int j = 0; j < k; j++) m[i, j] = 1 | 2 | 4 | 8;
            d.Push((r.Next(c), r.Next(k))); m[d.Peek().Item1, d.Peek().Item2] |= 16; int g = 1;
            while (g > 0)
            {
                var C = d.Peek(); var b = new System.Collections.Generic.List<(int, int, int)>();
                if (C.Item1 > 0 && (m[C.Item1 - 1, C.Item2] & 16) == 0) b.Add((C.Item1 - 1, C.Item2, 1));
                if (C.Item1 < c - 1 && (m[C.Item1 + 1, C.Item2] & 16) == 0) b.Add((C.Item1 + 1, C.Item2, 2));
                if (C.Item2 > 0 && (m[C.Item1, C.Item2 - 1] & 16) == 0) b.Add((C.Item1, C.Item2 - 1, 4));
                if (C.Item2 < k - 1 && (m[C.Item1, C.Item2 + 1] & 16) == 0) b.Add((C.Item1, C.Item2 + 1, 8));
                if (b.Count > 0)
                {
                    var K = b[r.Next(b.Count)]; (int, int) M = (K.Item1, K.Item2);
                    m[C.Item1, C.Item2] ^= (K.Item3 == 1 ? 8 : K.Item3 == 2 ? 2 : K.Item3 == 4 ? 1 : 4);
                    m[M.Item1, M.Item2] |= 16;
                    m[M.Item1, M.Item2] ^= (K.Item3 == 1 ? 2 : K.Item3 == 2 ? 8 : K.Item3 == 4 ? 4 : 1);
                    d.Push(M);
                }
                else { d.Pop(); }
                g = d.Count;
            }
            return m;
        }
    }
}