uses math;

// вычисление значения кривой в точке x
function f(x: double): double;
begin
  f := 2 * x * x * x - x * x + 3 * x + 4;
end;

// вычисление интеграла методом трапеций
function area(a, b: double; n: integer): double;
var
  h, sum: double;
  i: integer;
begin
  h := (b - a) / n;
  sum := (f(a) + f(b)) / 2;  
  for i := 1 to n - 1 do 
    sum := sum + f(a + i * h); 
  area := abs(sum * h);
end;

// оценка погрешности
procedure find_error(a, b: double; n: integer; var error: double);
var
  area_n, area_2n: double;
begin
  area_n := area(a, b, n);
  area_2n := area(a, b, n * 2);
  error := abs(area_2n - area_n);
end;

var
  a, b, res, error, proc: double;
  lm, nm, im, em, n, punct: integer;
begin
  lm:=0; nm:=0; im:=0; em:=0;
  repeat
    writeln('Меню');
    write('1. Ввести пределы (a, b) ');
    if lm = 1 then write(a:0:3, ' ', b:0:3);
    writeln();
    write('2. Ввести количество разбиений (n) ');
    if nm = 1 then write(n);
    writeln();
    write('3. Вычислить интеграл ');
    if im = 1 then write(res:0:6);
    writeln();
    write('4. Оценить погрешность ');
    if (em = 1) and (res > 0) then
    begin
      proc := (1 - abs(res - error) / res) * 100;
      write(error:0:6, ' ', proc:0:6, '%');
    end;
    writeln();
    writeln('5. Выход');
    read(punct);
      case punct of
        1: begin
          writeln('Введите пределы: ');
          lm := 0;
          readln(a, b);
            if a < 0 then
            begin
              a := 0;
              writeln('Предел a был изменён на 0');
            end;
            if b >= a then lm := 1
            else writeln('Неверный ввод: b должно быть больше либо равно a');
            im:=0; em:=0;
        end;
        2: begin
          writeln('Введите количество разбиений: ');
          nm := 0;
          readln(n);
          if n > 0 then nm := 1
          else writeln('Ошибка ввода: n должно быть больше нуля');
          im:=0; em:=0;
        end;
        3: begin
          if (lm = 1) and (nm = 1) then
            begin
             res := area(a, b, n);
             im := 1;
            end
            else writeln('Данные не введены!');
        end;
        4: begin
          if (lm = 1) and (nm = 1) then
          begin
            res := area(a, b, n);
            find_error(a, b, n, error);
            em := 1;
          end 
          else writeln('Данные не введены!');
        end;
        5: begin
          exit;
        end;
        else writeln('Неверный ввод');   
      end;
  until punct = 5;
end.