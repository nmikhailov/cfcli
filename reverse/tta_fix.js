var Table=["length","charCodeAt","floor"];
    function calcTta (arg){
        var sum=0;
        for(var i=0; i < arg.length; i++){
            sum = (sum + (i + 1) * (i + 2) * arg.charCodeAt(i)) % 1009;
            if(i % 3 == 0){
                sum++;
            }
            if(i % 2 == 0){
                sum *= 2;
            }
            if(i > 0){
                sum -= Math.floor(arg.charCodeAt((Math.floor(i / 2)) / 2) * (sum % 5));
            }
            while(sum < 0){
                sum += 1009;
            }
            while(sum >= 1009){
                sum -= 1009;
            }
         }
      return sum;
    }

    this.signForms = function () {
        var etc = Codeforces.tta();
        if (etc) {
            $("form").each(function () {
                var f = $(this);
                var upd = 0;
                f.find("input[name='_tta']").each(function () {
                    upd++;
                    $(this).val(etc);
                });
                if (upd == 0) {
                    f.append("<input type='hidden' name='_tta' value='" + etc + "'/>");
                }
            });
        }
    }

    this.tta = function() {
        return calcTta(Codeforces.getCookie("39ce7"));
    }
