var
  x, i, xx: integer;
  n: string;
begin
  readln(x);
  if x = 0 then 
    begin
      writeln(0);
      halt;
    end;  
  n := '';
  xx := abs(x);
  while xx > 0 do
  begin
    if (xx+1) mod 3 = 0 then 
      begin
        insert('n', n, -1);
        xx := (xx+1) div 3;
      end
    else if (xx-1) mod 3 = 0 then 
      begin
        insert('p', n, -1);
        xx := (xx-1) div 3;
      end
    else 
      begin
        insert('0', n, -1);
        xx := xx div 3;
      end;
  end;
  if x < 0 then 
  begin
    for i:=1 to (length(n)) do
    begin
      if n[i] = 'n' then n[i] := 'p'
      else if n[i] = 'p' then n[i] := 'n';      
    end;
  end;
  writeln(n);
end.