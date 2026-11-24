public int[,] R(int c, int k, System.Random r) 
{
    var m = new int[c, k];
    var d = new System.Collections.Generic.Stack<(int, int)>();
    for (int i = 0; i < c; i++)
        for (int j = 0; j < k; j++)
            m[i, j] = 15;

    var S = (r.Next(c), r.Next(k));
    d.Push(S);
    m[S.Item1, S.Item2] |= 16; 

    while (d.Count > 0)
    {
        var C = d.Peek();
        var b = new System.Collections.Generic.List<(int, int, int)>();

        if (C.Item1 > 0 && (m[C.Item1 - 1, C.Item2] & 16) == 0) b.Add((C.Item1 - 1, C.Item2, 1));
        if (C.Item1 < c - 1 && (m[C.Item1 + 1, C.Item2] & 16) == 0) b.Add((C.Item1 + 1, C.Item2, 2));
        if (C.Item2 > 0 && (m[C.Item1, C.Item2 - 1] & 16) == 0) b.Add((C.Item1, C.Item2 - 1, 4));
        if (C.Item2 < k - 1 && (m[C.Item1, C.Item2 + 1] & 16) == 0) b.Add((C.Item1, C.Item2 + 1, 8));

        if (b.Count > 0)
        {
            var K = b[r.Next(b.Count)];
            var N = (K.Item1, K.Item2);
            int D = K.Item3;
            m[C.Item1, C.Item2] ^= D;
            m[N.Item1, N.Item2] ^= (D == 1 ? 2 : D == 2 ? 1 : D == 4 ? 8 : 4);

            m[N.Item1, N.Item2] |= 16;
            
            d.Push(N);
        }
        else
        {
            d.Pop();
        }
    }
    return m;
}