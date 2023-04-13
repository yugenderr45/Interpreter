
begin
    int n
    int i
    int array[10]
    i:=1
    n:=10
    while(i<=n)
    begin
        array:=insert
        i:=i+1
    end
    array:=rev
    print(array)
end

int rev(int array[],int n)
    begin
    int start
    int stop
    start:=1
    stop:=n
    while(start<stop)
        begin
        array[start]:=:arr[stop]
        start:=start+1
        stop:=stop-1
        end
    end

