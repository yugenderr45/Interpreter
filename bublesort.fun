
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
    array:=bublesort
    print(array)
end

int bublesort(int array[],int n)
   begin
      int i
      int j
      i:=1
   while(i<=n)
      begin
         j:=1
         while(j<=n)
            begin
            if(array[j]>array[j]+1)
               begin
                  array[j]:=:array[j]

               end
                                
                  j:=j+1
            end
             i:=i+1
      end 
   end
