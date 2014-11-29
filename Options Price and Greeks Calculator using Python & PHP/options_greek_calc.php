<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>

    <body>
        <form action="" method="post">
        <label>Enter Stock Price:</label>
        <input type="text" name="sto_pr" /><br>
        <label>Enter Strike Price :</label>
        <input type="text" name="str_pr" /><br><br>
        <label>Enter Interest rate:</label>
        <input type="text" name="irate" /><br><br>
        <label>Enter Time to Maturity:</label>
        <input type="text" name="timem" /><br><br>
        <label>Enter Volatility:</label>
        <input type="text" name="vola" /><br><br>
        <label>Enter Dividend Yeild:</label>
        <input type="text" name="div_yld" /><br><br>
        <input  type="submit" name="btn_submit" value="Calculate">
        </form>

        <?php
            if(isset($_POST['btn_submit']))
            {
                $num1 = $_POST['sto_pr'];
                $num2 = $_POST['str_pr'];
                $num3 = $_POST['irate'];
                $num4 = $_POST['timem'];
                $num5 = $_POST['vola'];
                $num6 = $_POST['div_yld'];
                
                #$data = array($num1,$num2);
                $result = exec("python /home/vivek/Python/optionscalculator/basic.py $num1 $num2 $num3 $num4 $num5 $num6");
                $total = json_decode($result, true);
                echo "Call Price : ".$total['call_price'];
                echo "<br>Put Price : " .$total['put_price'];
                echo "<br> Delta Call: " .$total['delta_call'];
                echo "<br> Delta Put: " .$total['delta_put'];
                echo "<br> Gamma: " .$total['gamma'];
                echo "<br> Theta Call: " .$total['theta_call'];
                echo "<br> Theta Put: " .$total['theta_put'];
                echo "<br> Vega: " .$total['vega'];
                echo "<br> Rho Call: " .$total['rho_call'];
                echo "<br> Rho Put: " .$total['rho_put'];
            }
        ?>
    </body>
</html>