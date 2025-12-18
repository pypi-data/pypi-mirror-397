import pytest
import glob
import os
from pathlib import Path
from yuip import YuiParser, YuiRuntime, YuiArray, YuiError
from yuip.yui import FunctionNode

class TestYuiError:
    """YuiError のテストクラス"""
    
    def test_formatted_message(self):
        """YuiError のメッセージ表示をテスト"""
        code_map = ("x = 1 + \n y = 2", 6, 6)
        e = YuiError("エラーメッセージ", code_map=code_map)
        assert "^" in str(e.formatted_message())

class TestYuiArray:
    """YuiArray のテストクラス"""
    
    def test_array_list(self):
        """YuiArray の初期化をテスト"""
        arr = YuiArray([1, 2, 3])
        assert len(arr.elements) == 3
        assert arr.elements[0] == 1
        assert arr.elements[1] == 2
        assert arr.elements[2] == 3

    def test_array_string(self):
        """YuiArray の文字列をテスト"""
        arr = YuiArray("123.45")
        print(arr.elements)
        assert len(arr.elements) == 6
        assert arr.elements[0] == 49
        assert arr.elements[1] == 50
        assert arr.elements[2] == 51
        assert arr.elements[3] == 46
        assert arr.elements[4] == 52
        assert arr.elements[5] == 53

    def test_array_float(self):
        """YuiArray の浮動小数点数をテスト"""
        arr = YuiArray(23.45)
        print(arr.elements)
        assert arr.elements[0] == 1
        assert arr.to_float() == 23.45

class TestExpression:
    """YuiParser のテストクラス"""

    def test_int(self):
        """単純な式のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec("1", eval_mode=True)
        assert result == 1

    def test_negative_int(self):
        """単純な式のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec("-1", eval_mode=True)
        assert result == -1

    def test_string(self):
        """文字列のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('"hello"', eval_mode=True)
        assert result == "hello"

    def test_empty_string(self):
        """空の文字列のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('""', eval_mode=True)
        assert result == ""
    
    def test_char(self):
        """文字のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('"A"[0]', eval_mode=True)
        assert result == 65

    def test_char2(self):
        """文字のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('"あ"[0]', eval_mode=True)
        assert result == 12354

    def test_empty_array(self):
        """空の配列のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('[]', eval_mode=True)
        assert result == []

    def test_int_array(self):
        """整数の配列のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('[1,2,3]', eval_mode=True)
        assert result == [1,2,3]

    def test_array_array(self):
        """配列の配列のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('[[1,2], [3,4]]', eval_mode=True)
        assert result == [[1,2], [3,4]]

    def test_variable(self):
        """変数のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x', env={'x': 1}, eval_mode=True)
        assert result == 1

    def test_array_length(self):
        """配列の大きさのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('|x|', env={'x': [1, 2, 3]}, eval_mode=True)
        assert result == 3

    def test_array_index(self):
        """配列のインデックスのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x[0]', env={'x': [1, 2, 3]}, eval_mode=True)
        assert result == 1

    def test_2darray_index(self):
        """2次元配列のインデックスのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x[0]', env={'x': [[1, 2], [3, 4]]}, eval_mode=True)
        assert result == [1,2]
        result = runtime.exec('x[0][1]', env={'x': [[1, 2], [3, 4]]}, eval_mode=True)
        assert result == 2

    def test_null(self):
        """nullのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('?', eval_mode=True)
        assert result == None

    def test_function(self):
        """関数のパースをテスト"""
        runtime = YuiRuntime()
        with pytest.raises(YuiError) as e:
            result = runtime.exec('和(1,2,3)', eval_mode=True)
            assert result == 6
        assert '標準' in str(e.value)

    def test_vardecl(self):
        """変数定義のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=0\nx', eval_mode=True)
        assert result == 0

    def test_array_decl(self):
        """配列定義のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=[0]\nx', eval_mode=True)
        assert result == [0]

    def test_variable_update(self):
        """変数更新のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=0\nx=1\nx', eval_mode=True)
        assert result == 1

    def test_increment(self):
        """インクリメントのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=0\nxを増やす\nx', eval_mode=True)
        assert result == 1

    def test_decrement(self):
        """デクリメントのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=1\nxを減らす\nx', eval_mode=True)
        assert result == 0

    def test_array_update(self):
        """配列更新のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=[0]\nx[0]=1\nx[0]', eval_mode=True)
        assert result == 1

    def test_array_increment(self):
        """配列インクリメントのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=[0]\nx[0]を増やす\nx[0]', eval_mode=True)
        assert result == 1

    def test_array_decrement(self):
        """配列デクリメントのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=[1]\nx[0]を減らす\nx[0]', eval_mode=True)
        assert result == 0

    def test_parse_2darray_update(self):
        """配列更新のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=[[0]]\nx[0][0]=1\nx[0][0]', eval_mode=True)
        assert result == 1

    def test_2darray_increment(self):
        """配列インクリメントのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=[[0]]\nx[0][0]を増やす\nx[0][0]', eval_mode=True)
        assert result == 1

    def test_2darray_decrement(self):
        """配列デクリメントのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=[[1]]\nx[0][0]を減らす\nx[0][0]', eval_mode=True)
        assert result == 0

    def test_array_append(self):
        """配列追加のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=[]\nxの末尾に1を追加する\nx[0]', eval_mode=True)
        assert result == 1

    def test_repeat_5_times(self):
        """5回くり返すのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=0\n5回くり返す{\nxを増やす\n}\nx', eval_mode=True)
        assert result == 5

    def test_if(self):
        """ルールのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=0\nもしxが0ならば{\nx=1\n}\nx', eval_mode=True)
        assert result == 1

    def test_if_else(self):
        """ルールのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=0\nもしxが1ならば{\nx=1\n}\nそうでなければ{\nx=2\n}\nx', eval_mode=True)
        assert result == 2

    def test_if_not(self):
        """ルールのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=1\nもしxが0以外ならば{\nx=0\n}\nx', eval_mode=True)
        assert result == 0

    def test_if_not_else(self):
        """ルールのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=0\nもしxが0以外ならば{\nx=0\n}\nそうでなければ{\nx=2\n}\nx', eval_mode=True)
        assert result == 2

    def test_if_else_if(self):
        """ルールのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=1\nもしxが1ならば{\nx=-1\n}\nそうでなければ{\nもしxが2ならば{\nx=-2\n}\nそうでなければ{\nx=0\n}\n}\nx', eval_mode=True)
        assert result == -1

    def test_if_else_if2(self):
        """ルールのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=2\nもしxが1ならば{\nx=-1\n}\nそうでなければ{\nもしxが2ならば{\nx=-2\n}\nそうでなければ{\nx=0\n}\n}\nx', eval_mode=True)
        assert result == -2

    def test_if_else_if3(self):
        """ルールのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=3\nもしxが1ならば{\nx=-1\n}\nそうでなければ{\nもしxが2ならば{\nx=-2\n}\nそうでなければ{\nx=0\n}\n}\nx', eval_mode=True)
        assert result == 0

    def test_if_lt(self):
        """ルールのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=-1\nもしxが0より小さいならば{\nx=0\n}\nx', eval_mode=True)
        assert result == 0

    def test_if_lt2(self):
        """ルールのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=0\nもしxが0より小さいならば{\nx=-1\n}\nx', eval_mode=True)
        assert result == 0

    def test_if_lte(self):
        """ルールのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=-1\nもしxが0以下ならば{\nx=1\n}\nx', eval_mode=True)
        assert result == 1

    def test_if_lte2(self):
        """ルールのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=0\nもしxが0以下ならば{\nx=1\n}\nx', eval_mode=True)
        assert result == 1

    def test_if_lte3(self):
        """ルールのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=1\nもしxが0以下ならば{\nx=2\n}\nx', eval_mode=True)
        assert result == 1

    def test_if_gt(self):
        """ルールのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=1\nもしxが0より大きいならば{\nx=0\n}\nx', eval_mode=True)
        assert result == 0

    def test_if_gt2(self):
        """ルールのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=0\nもしxが0より大きいならば{\nx=-0\n}\nx', eval_mode=True)
        assert result == 0

    def test_if_gte(self):
        """ルールのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=1\nもしxが0以上ならば{\nx=-1\n}\nx', eval_mode=True)
        assert result == -1

    def test_if_gte2(self):
        """ルールのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=0\nもしxが0以上ならば{\nx=-1\n}\nx', eval_mode=True)
        assert result == -1

    def test_if_gte3(self):
        """ルールのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=-1\nもしxが0以上ならば{\nx=1\n}\nx', eval_mode=True)
        assert result == -1

class TestDecimal:

    def test_decimal(self):
        """単純な式のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec("1.0", eval_mode=True)
        assert result == 1.0

    def test_negative_decimal(self):
        """単純な式のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec("-1.0", eval_mode=True)
        assert result == -1.0

    def test_variable(self):
        """少数のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=1.2\nx', eval_mode=True)
        assert result == 1.2

    def test_minimum(self):
        """少数のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=0.0001\nx', eval_mode=True)
        assert result == 0.0001

    def test_under_minimum(self):
        """ゆいの最小精度以下の少数のパースをテスト"""
        with pytest.raises(YuiError) as e:
            runtime = YuiRuntime()
            result = runtime.exec('x=0.00001\nx', eval_mode=True)
            assert result == 0.00001
        assert "精度" in str(e.value)

class TestZenkaku:
    """YuiParser のテストクラス"""

    def test_int(self):
        """単純な式のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec("１", eval_mode=True)
        assert result == 1

    def test_negative_int(self):
        """単純な式のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec("-１", eval_mode=True)
        assert result == -1

    def test_string(self):
        """文字列のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('＂hello＂', eval_mode=True)
        assert result == "hello"

    def test_empty_array(self):
        """空の配列のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('［］', eval_mode=True)
        assert result == []

    def test_int_array(self):
        """整数の配列のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('［１、２、３］', eval_mode=True)
        assert result == [1,2,3]

    def test_variable(self):
        """変数のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('ｘ', env={'x': 1}, eval_mode=True)
        assert result == 1

    def test_array_length(self):
        """配列の大きさのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('｜x｜', env={'x': [1, 2, 3]}, eval_mode=True)
        assert result == 3

    def test_array_index(self):
        """配列のインデックスのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('ｘ［０］', env={'x': [1, 2, 3]}, eval_mode=True)
        assert result == 1

    def test_null(self):
        """nullのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('？', eval_mode=True)
        assert result == None

    def test_vardecl(self):
        """変数定義のパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('ｘ＝０\nｘ', eval_mode=True)
        assert result == 0


class TestVariableName:
    def test_変数(self):
        """日本語の変数名のパースをテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('変数=1\n変数', eval_mode=True)
        assert result == 1

    def test_近い要素がある(self):
        """日本語の変数名のパースをテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('近い要素がある=1\n近い要素がある', eval_mode=True)
        assert result == 1

    def test_残りの回数(self):
        """日本語の変数名のパースをテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('残りの回数=1\n残りの回数', eval_mode=True)
        assert result == 1

    def test_文字列(self):
        """日本語の変数名のパースをテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('文字列ROT13="こんにちは"\n文字列ROT13', eval_mode=True)
        assert result == "こんにちは"

class TestParser:

    def test_comma(self):
        """コンマのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=0\n5回，くり返す{\nxを増やす\n}\nx', eval_mode=True)
        assert result == 5

    def test_comma2(self):
        """コンマのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=0\n5回，くり返す{\nxを増やす\n}\nx', eval_mode=True)
        assert result == 5

    def test_comma3(self):
        """コンマのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=0\n5回,くり返す{\nxを増やす\n}\nx', eval_mode=True)
        assert result == 5

    def test_comma4(self):
        """コンマのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('x=0\n5回､くり返す{\nxを増やす\n}\nx', eval_mode=True)
        assert result == 5

    def test_argument_comma1(self):
        """コンマのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('f=入力x、yに対し{\n}\nf(1、2)', eval_mode=True)
        assert 'x' in result
        assert 'y' in result

    def test_argument_comma2(self):
        """全角コンマのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('f=入力x，yに対し{\n}\nf(1，2)', eval_mode=True)
        assert 'x' in result
        assert 'y' in result

    def test_argument_comma3(self):
        """半角コンマのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('f=入力x､yに対し{\n}\nf(1､2)', eval_mode=True)
        assert 'x' in result
        assert 'y' in result

    def test_array_comma1(self):
        """コンマのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('[1、2]', eval_mode=True)
        assert result == [1, 2]

    def test_array_comma2(self):
        """コンマのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('[1，2]', eval_mode=True)
        assert result == [1, 2]

    def test_array_comma3(self):
        """コンマのパースをテスト"""
        runtime = YuiRuntime()
        result = runtime.exec('[1､2]', eval_mode=True)
        assert result == [1, 2]

    def test_array_comma(self):
        """配列のパースをテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('[1, 2,]', eval_mode=True)
        assert result == [1, 2]

    def test_array_comment(self):
        """配列のパースをテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('[\n1,\n 2, #コメント\n]\n', eval_mode=True)
        assert result == [1, 2]

    def test_parse_2darray(self):
        """2次元配列のパースをテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('[\n  [1, 2],\n   [3, 4]\n]', eval_mode=True)
        assert result == [[1, 2], [3, 4]]

    def test_parse_2darray(self):
        """文字列配列のパースをテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('["AB", "CD"]', eval_mode=True)
        assert result == ["AB", "CD"]

    def test_parse_if_empty(self):
        """空のif文のパースをテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('x=0\nもしxが0ならば{\n}\nx', eval_mode=True)
        assert result == 0

    def test_parse_if_empty2(self):
        """空のif文のパースをテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('x=0\nもしxが0ならば{\n\n}\nx', eval_mode=True)
        assert result == 0

    def test_parse_if_empty_comment(self):
        """空のif文のパースをテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('x=0\nもしxが0ならば{\n#何もしない\n}\nx', eval_mode=True)
        assert result == 0

class TestSyntaxError:
    """構文エラーのテストクラス"""

    def test_parse_assignment(self):
        """代入文のパースをテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            env = runtime.exec('x = ')
        assert "忘" in str(e.value)

    def test_parse_assignment(self):
        """代入文のパースをテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            env = runtime.exec('xを1とする')
        assert "知" in str(e.value)

    def test_差分に対し(self):
        """日本語の変数名のパースをテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            result = runtime.exec('差分に対し=1\n差分に対し', eval_mode=True)
        assert "変数名" in str(e.value) or "別" in str(e.value)

    # def test_末尾に(self):
    #     """日本語の変数名のパースをテスト"""
    #     with pytest.raises(YuiError) as e:
    #         runtime: YuiRuntime = YuiRuntime()
    #         result = runtime.exec('配列=[]\n配列に1を追加する', eval_mode=True)
    #     assert "末尾" in str(e.value)

    def test_parse_infix(self):
        """中置記法をテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            result = runtime.exec('x\n4+2')
            assert result == 6
        assert "中置" in str(e.value)
        assert e.value.lineno == 2

    def test_parse_fraction(self):
        """少数をテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            result = runtime.exec('4.', eval_mode=True)
            assert result == 4.0
        assert "数" in str(e.value)

    def test_parse_unclosed_string(self):
        """未閉じ文字列のパースをテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            expression = runtime.exec('x\n"AB')
        assert "閉" in str(e.value)
        assert e.value.lineno == 2

    def test_parse_unclosed_array(self):
        """未閉じ配列のパースをテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            result = runtime.exec('x\n[1, 2, 3')
        assert "閉" in str(e.value)
        assert e.value.lineno == 2

    def test_parse_unclosed_array2(self):
        """未閉じ配列のパースをテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            result = runtime.exec('x\n[1, 2,')
        assert "閉" in str(e.value) or "忘" in str(e.value)
        assert e.value.lineno == 2

    def test_parse_no_comma_in_array(self):
        """未閉じ配列のパースをテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            result = runtime.exec('x\n[1, 2 3]')
        assert "閉" in str(e.value)
        assert e.value.lineno == 2

    def test_parse_if(self):
        """if文のパースをテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            result = runtime.exec('x=0\nもしxならば{\nx', eval_mode=True)
        assert "が" in str(e.value)
        assert e.value.lineno == 2

    def test_parse_if2(self):
        """if文のパースをテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            result = runtime.exec('x=0\nもしならば{\nx', eval_mode=True)
        assert "比較" in str(e.value)
        assert e.value.lineno == 2

    def test_parse_if3(self):
        """if文のパースをテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            result = runtime.exec('x=0\nもしxがならば{\nx', eval_mode=True)
        assert "比較" in str(e.value)
        assert e.value.lineno == 2

    def test_parse_未満(self):
        """if文のパースをテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            result = runtime.exec('x=0\nもしxが0未満ならば{\nx', eval_mode=True)
        assert "未満" in str(e.value)
        assert e.value.lineno == 2

    def test_parse_unclosed_if(self):
        """未閉じif文のパースをテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            result = runtime.exec('x=0\nもしxが0ならば{\nx', eval_mode=True)
        assert "閉" in str(e.value)
        assert e.value.lineno == 2

    def test_parse_unclosed_else(self):
        """未閉じelse文のパースをテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            result = runtime.exec('x=0\nもしxが0ならば{\n}\nそうでなければ{\nx', eval_mode=True)
        assert "閉" in str(e.value)
        assert e.value.lineno == 4

    def test_parse_unclosed_repeat(self):
        """未閉じ繰り返し文のパースをテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            result = runtime.exec('x=0\nx回、くり返す{\nx', eval_mode=True)
        assert "閉" in str(e.value)
        assert e.value.lineno == 2

    def test_parse_unclosed_function(self):
        """未閉じ関数のパースをテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            result = runtime.exec('x=入力 xに対し{\nx', eval_mode=True)
        assert "閉" in str(e.value)
        assert e.value.lineno == 1

    def test_parse_break(self):
        """変な位置のbreakのパースをテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            result = runtime.exec('くり返しを抜ける', eval_mode=True)
        assert "内側" in str(e.value)
        assert e.value.lineno == 1

    def test_parse_return(self):
        """変な位置のreturnのパースをテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            result = runtime.exec('0が答え', eval_mode=True)
        assert "内側" in str(e.value)
        assert e.value.lineno == 1


class TestRuntimeError:
    """実行時エラーのテストクラス"""
    
    def test_variable_not_defined(self):
        """未定義変数のテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            env = runtime.exec('x=0\ny', eval_mode=True)
        assert "変数" in str(e.value)
        assert e.value.lineno == 2

    def test_variable_not_defined(self):
        """未定義変数のテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            env = runtime.exec('x=0\nyを減らす', eval_mode=True)
        assert "変数" in str(e.value)
        assert e.value.lineno == 2

    def test_append_number(self):
        """アペンドのパースをテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            env = runtime.exec('x=1\nxの末尾に1を追加する')
        assert "配列" in str(e.value)

    def test_number_index(self):
        """数値の配列アクセスのテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            env = runtime.exec('x = 1\nx[3]', eval_mode=True)
        assert "配列" in str(e.value)

    def test_number_length(self):
        """数値の配列アクセスのテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            env = runtime.exec('x = 1\n|3|', eval_mode=True)
        assert "配列" in str(e.value)

    def test_empty_array_index_out_of_range(self):
        """配列の範囲外アクセスのテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            env = runtime.exec('x = []\nx[3]', eval_mode=True)
        assert "空" in str(e.value)

    def test_array_index_out_of_range(self):
        """配列の範囲外アクセスのテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            env = runtime.exec('x = [1,2,3]\nx[3]', eval_mode=True)
        assert "添え字" in str(e.value)

    def test_string_index_out_of_range(self):
        """文字列の範囲外アクセスのテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            env = runtime.exec('x = "abc"\nx[3]', eval_mode=True)
        assert "添え字" in str(e.value)


class TestLoop:
    """ループ検出のテストクラス"""
    
    def test_loop(self):
        """くり返しのパースをテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('x=0\n10回くり返す{\nxを増やす\n}\nx', eval_mode=True)
        assert result == 10

    def test_variable_loop(self):
        """くり返しのパースをテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('x=1\nx回くり返す{\nxを増やす\n}\nx', eval_mode=True)
        assert result == 2

    def test_multi_loop(self):
        """くり返しのパースをテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('x=0\n10回くり返す{\n10回くり返す{\n10回くり返す{\nxを増やす\n}\n}\n}\nx', eval_mode=True)
        assert result == 1000

    def test_break(self):
        """くり返しのパースをテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('x=0\n10回、くり返す{\nくり返しを抜ける\nxを増やす\n}\nx', eval_mode=True)
        assert result == 0

    def test_infinite_loop(self):
        """無限ループ検出のテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            env = runtime.exec('x=0\n?回くり返す{\nxを増やす\n}', timeout=1, eval_mode=True)
        assert "タイムアウト" in str(e.value)

    def test_negative_loop(self):
        """無限ループ検出のテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            env = runtime.exec('x=-10\nx回くり返す{\nxを増やす\n}', timeout=1, eval_mode=True)
        assert "整数" in str(e.value)

    def test_array_loop(self):
        """無限ループ検出のテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            env = runtime.exec('x=[1,2]\nx回くり返す{\nxを増やす\n}', timeout=1, eval_mode=True)
        assert "囲" in str(e.value)


class TestFunction:
    """関数定義のテストクラス"""
    def test_definition(self):
        """関数定義のパースをテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('f = 入力 x に対し {\nxが答え\n}\nf(1)', eval_mode=True)
        assert result == 1

    def test_no_return(self):
        """関数定義ノーリターンのパースをテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('f = 入力 x,y に対し {\n\n}\nf(1,2)', eval_mode=True)
        assert 'x' in result
        assert 'y' in result

    def test_abs(self):
        """絶対値関数のパースをテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('abs = 入力 x に対し {\nもしxが0以下ならば{\n-xが答え\n}\nそうでなければ{\nxが答え\n}\n}\nabs(-1)', eval_mode=True)
        assert result == 1

    def test_abs2(self):
        """絶対値関数のパースをテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('abs = 入力 x に対し {\nもしxが0以下ならば{\n-xが答え\n}\nxが答え\n}\nabs(-1)', eval_mode=True)
        assert result == 1

    def test_exp(self):
        """累乗定義のパースをテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('exp = 入力 x に対し {\nz=0\nx回くり返す{\nx回くり返す{\nzを増やす\n}\n}\nzが答え\n}\nexp(3)', eval_mode=True)
        assert result == 9

    def test_addition(self):
        """足し算関数のテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('''
足し算 = 入力 X, Y に対し {
    Y回、くり返す {
        Xを増やす
    }
    Xが答え
}

# 次はどうなるでしょうか？
X = 足し算(10, 5)

# 次はどうなるのでしょうか？
足し算(足し算(1, 2), 3)''', eval_mode=True)
        assert result == 6

    def test_mod(self):
        """あまり関数のテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('''
あまり = 入力 X, Y に対し {
    X回、くり返す {
        R = 0
        Y回、くり返す {
            もしXが0ならば、{
                Rが答え
            }
            Rを増やす
            Xを減らす
        }
    }
}

# 次はどうなるでしょうか？
あまり(60, 48)''', eval_mode=True)
        assert result == 12

    def test_gcd(self):
        """gcd関数のテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('''
# GCD

最大公約数 = 入力 X, Y に対し {
    Y回、くり返す {
        R = あまり(X, Y)
        もしRが0ならば、{
            Yが答え
        }
        X = Y
        Y = R
    }
}
                                    
あまり = 入力 X, Y に対し {
    X回、くり返す {
        R = 0
        Y回、くり返す {
            もしXが0ならば、{
                Rが答え
            }
            Rを増やす
            Xを減らす
        }
    }
}

# 次はどうなるでしょうか？
最大公約数(6215, 4746)''', eval_mode=True)
        assert result == 113

    def test_rec(self):
        """再帰関数のテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('''
# 再帰関数による総和

足し算 = 入力 X, Y に対し {
    Y回、くり返す {
        Xを増やす
    }
    Xが答え
}

減らす = 入力 X に対し {
    Xを減らす
    Xが答え
}
                                    
総和 = 入力 n に対し {
    もし n が 1 ならば、{
        1が答え
    }
    そうでなければ、{
        足し算(総和(減らす(n)), n)が答え
    }
}

総和(4)''', eval_mode=True)
        assert result == 10

    def test_sum(self):
        """合計関数のテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('''
# 数列の合計

足し算 = 入力 X, Y に対し {
    Y回、くり返す {
        Xを増やす
    }
    Xが答え
}

合計 = 入力 数列 に対し {
    i = 0
    sum = 0
    |数列|回、くり返す {
        sum = 足し算(sum, 数列[i])
        iを増やす
    }
    sumが答え
}

合計([1, 2, 3, 4, 5])
''', eval_mode=True)
        assert result == 15

    def test_recursion_error(self):
        """関数定義のパースをテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            result = runtime.exec('f = 入力 x に対し {\nf(x)が答え\n}\nf(1)', eval_mode=True)
            assert result == 1
        assert e.value.lineno == 2
        assert '再帰' in str(e.value)

    def test_too_much_arguments(self):
        """関数定義のパースをテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            result = runtime.exec('f = 入力 x に対し {\n1が答え\n}\nf(1,2)', eval_mode=True)
            assert result == 1
        assert e.value.lineno == 4
        assert '引数' in str(e.value)

    def test_too_less_arguments(self):
        """関数定義のパースをテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            result = runtime.exec('f = 入力 x に対し {\n1が答え\n}\nf()', eval_mode=True)
            assert result == 1
        assert e.value.lineno == 4
        assert '引数' in str(e.value)

    def test_error_in_function(self):
        """関数定義のパースをテスト"""
        with pytest.raises(YuiError) as e:
            runtime: YuiRuntime = YuiRuntime()
            result = runtime.exec('x=0\nf = 入力 x に対し {\n yを増やす\n 1が答え\n}\nf(1)', eval_mode=True)
            assert result == 1
        assert e.value.lineno == 3
        assert '知らない' in str(e.value)


class TestStandardLibrary:
    """ライブラリのテストクラス"""
    def test_using_library(self):
        """nullのパースをテスト"""
        runtime: YuiRuntime = YuiRuntime()
        env = runtime.exec('標準ライブラリを使う')
        assert '和' in env

    def test_using_abs(self):
        """絶対値のパースをテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('標準ライブラリを使う\n絶対値(-1)', eval_mode=True)
        assert result == 1

    def test_abs_error(self):
        """絶対値のパースをテスト"""
        runtime: YuiRuntime = YuiRuntime()
        with pytest.raises(YuiError) as e:
            result = runtime.exec('標準ライブラリを使う\n絶対値(-1, -1)', eval_mode=True)
            print(e.formatted_message())
            assert result == 1
        assert e.value.lineno == 2
        assert '関数' in str(e.value)

    def test_using_sum(self):
        """和のパースをテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('標準ライブラリを使う\n和(1,2)', eval_mode=True)
        assert result == 3
        result = runtime.exec('標準ライブラリを使う\n和(1,2,3)', eval_mode=True)
        assert result == 6

    def test_using_sub(self):
        """差をテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('標準ライブラリを使う\n差(5,3)', eval_mode=True)
        assert result == 2
        result = runtime.exec('標準ライブラリを使う\n差(5,3,1)', eval_mode=True)
        assert result == 1

    def test_using_mul(self):
        """積をテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('標準ライブラリを使う\n積(2,3)', eval_mode=True)
        assert result == 6
        result = runtime.exec('標準ライブラリを使う\n積(2,3,4)', eval_mode=True)
        assert result == 24

    def test_using_div(self):
        """商をテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('標準ライブラリを使う\n商(4,2)', eval_mode=True)
        assert result == 2
        result = runtime.exec('標準ライブラリを使う\n商(8,2,2)', eval_mode=True)
        assert result == 2

    def test_using_mod(self):
        """剰余をテスト"""
        runtime: YuiRuntime = YuiRuntime()
        result = runtime.exec('標準ライブラリを使う\n剰余(4,3)', eval_mode=True)
        assert result == 1
        result = runtime.exec('標準ライブラリを使う\n剰余(14,5,3)', eval_mode=True)
        assert result == 1

class TestYuiEmitCode:
    """Yuiのコード生成テストクラス"""
    
    def test_emit_js(self):
        """コード変換のテスト"""
        parser = YuiParser()
        program = parser.parse(EMIT_YUI)
        code = program.emit("js", "|")
        print(code)
        assert code == EMIT_JS

    def test_emit_py(self):
        """コード変換のテスト"""
        parser = YuiParser()
        program = parser.parse(EMIT_YUI)
        code = program.emit("py", "|")
        print(code)
        assert code == EMIT_PYTHON

EMIT_YUI = """
合計 = 入力 数列 に対し {
    i = 0
    sum = 0
    buf = []
    |数列|回、くり返す {
        sum = 足し算(sum, 数列[i])
        もしsumが10より大きいならば、{
            buf[0] = 数列[i]
        }
        そうでなければ、{
            bufの末尾に数列[i]を追加する
        }
        ?回くり返す {
            sum = -sum
        }
        iを増やす
    }
    sumが答え
}
                                    
>>> 合計([1, 2, 3, 4, 5])
15
"""

EMIT_JS = """\
|合計 = function (数列) {
|    i = 0;
|    sum = 0;
|    buf = [];
|    for(var i1 = 0; i1 < (数列).length; i1++) {
|        sum = 足し算(sum, 数列[i]);
|        if(sum > 10) {
|            buf[0] = 数列[i];
|        }
|        else {
|            buf.push(数列[i]);
|        }
|        while(true) {
|            sum = -sum;
|        }
|        i += 1;
|    }
|    return sum;
|};
|console.assert(合計([1, 2, 3, 4, 5]) == 15);"""

EMIT_PYTHON = """\
|def 合計(数列):
|    i = 0
|    sum = 0
|    buf = []
|    for _ in range(len(数列)):
|        sum = 足し算(sum, 数列[i])
|        if sum > 10:
|            buf[0] = 数列[i]
|        else:
|            buf.append(数列[i])
|        while True:
|            sum = -sum
|        i += 1
|    return sum
|assert (合計([1, 2, 3, 4, 5]) == 15)"""