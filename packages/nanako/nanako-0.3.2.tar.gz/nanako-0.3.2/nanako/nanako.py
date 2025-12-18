"""
Yui (ゆい) 言語インタプリタ - 参照実装

このファイルは、Yui言語の完全な参照実装です。
生成AI時代のための教育用プログラミング言語として設計されています。

主要コンポーネント:
    1. データ構造 (YuiError, YuiArray)
    2. 標準ライブラリ (standard_library, arithmetic_library)
    3. ランタイム環境 (Environment, YuiRuntime)
    4. AST (抽象構文木) ノード (各種 Node クラス)
    5. パーサー (YuiParser)

設計思想:
    - 最小限の操作でチューリング完全性を実現
    - 日本語の自然な構文
    - 配列を中心としたデータモデル
    - わかりやすいエラーメッセージ
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Union
from types import FunctionType
from abc import ABC, abstractmethod
import time

# =============================================================================
# セクション 1: データ構造
# =============================================================================
# このセクションでは、Yui言語の基本的なデータ型とエラーハンドリングを定義します。
# - parse_error: エラー位置を人間が読める形式に変換
# - YuiError: Yui言語のエラーを表現するクラス
# - YuiArray: Yui言語の配列型（文字列、数値、配列を統一的に扱う）
# =============================================================================

def parse_error(text: str, pos: int) -> tuple:
    """
    ソースコード内の位置をエラー表示用の情報に変換する

    Args:
        text: ソースコード全体
        pos: エラーが発生した位置（文字インデックス）

    Returns:
        tuple: (text, line, col, snippet)
            - text: ソースコード全体
            - line: 行番号（1始まり）
            - col: 列番号（1始まり）
            - snippet: エラー行のコードスニペット

    Example:
        >>> text = "x = 1\\ny = 2\\nz"
        >>> parse_error(text, 10)
        ('x = 1\\ny = 2\\nz', 3, 1, 'z')
    """
    line = 1
    col = 1
    start = 0

    # エラー位置まで文字を辿り、行番号と列番号を計算
    for i, char in enumerate(text):
        if i == pos:
            break
        if char == '\n':
            line += 1
            col = 1
            start = i + 1
        else:
            col += 1

    # エラー行の終端を見つける
    end = text.find('\n', start)
    if end == -1:
        end = len(text)

    return text, line, col, text[start:end]


class YuiError(RuntimeError):
    """
    Yui言語のエラーを表現するクラス

    Yui言語では、すべてのエラーがこのクラスのインスタンスとして発生します。
    エラーメッセージだけでなく、ソースコードの位置情報も保持し、
    ユーザーに分かりやすいエラーメッセージを提供します。

    Attributes:
        source: エラーが発生したソースコード
        pos: エラー開始位置
        end_pos: エラー終了位置
        env: エラー発生時の環境（変数の状態）

    Example:
        >>> raise YuiError("変数が見つかりません", code_map)
    """
    source: str
    pos: Optional[int]
    end_pos: Optional[int]
    env: Optional[Dict[str, Any]]

    def __init__(self, message: str, code_map: Optional[tuple] = None,
                 env: Optional[Dict[str, Any]] = None):
        """
        YuiErrorを初期化する

        Args:
            message: エラーメッセージ
            code_map: (source, pos, end_pos) のタプル
            env: エラー発生時の環境
        """
        super().__init__(message)
        self.source = None
        self.pos = None
        self.end_pos = None
        self.env = None
        self.update_code_map(code_map, env)

    def update_code_map(self, code_map: tuple, env: Optional[Dict[str, Any]] = None):
        """
        エラーの位置情報を更新する

        エラーがキャッチされて再スローされる際に、
        より詳細な位置情報を追加するために使用されます。

        Args:
            code_map: (source, pos, end_pos) のタプル
            env: エラー発生時の環境
        """
        if code_map is not None:
            source = code_map[0]
            pos = code_map[1]
            end_pos = code_map[2]
            if self.source is None:
                self.source = source
            if self.pos is None:
                self.pos = pos
            if self.end_pos is None:
                self.end_pos = end_pos
        if self.env is not None:
            self.env = env

    @property
    def lineno(self) -> int:
        """エラー箇所の行番号を返す（1始まり）"""
        if self.source is not None and self.pos is not None:
            _, line, _, _ = parse_error(self.source, self.pos)
            return line
        return 0

    @property
    def offset(self) -> int:
        """エラー箇所の列番号を返す（1始まり）"""
        if self.source is not None and self.pos is not None:
            _, _, offset, _ = parse_error(self.source, self.pos)
            return offset
        return 0

    @property
    def text(self) -> str:
        """エラー箇所のコードスニペットを返す"""
        if self.source is not None and self.pos is not None:
            _, _, _, snippet = parse_error(self.source, self.pos)
            return snippet
        return ""

    def formatted_message(self, indent=" ", marker: str = '^') -> str:
        """
        エラーメッセージを整形して返す

        エラーメッセージに加えて、エラーが発生した行と位置を
        視覚的に表示します。

        Args:
            indent: インデント文字列
            marker: エラー位置を指すマーカー文字

        Returns:
            str: 整形されたエラーメッセージ

        Example:
            >>> error.formatted_message()
            '変数が見つかりません line 2, column 5:
             x = unknown_var
                 ^^^^'
        """
        message = self.args[0]
        if self.source is not None and self.pos is not None:
            source, line, col, snippet = parse_error(self.source, self.pos)
            # エラー範囲の長さを計算（最小4文字）
            length = max(self.end_pos - self.pos, 4) if self.end_pos is not None else 4
            # エラー位置を指すポインタを作成
            make_pointer = ' ' * (col - 1) + marker * length
            return f"{message} line {line}, column {col}:\n{indent}{snippet.strip()}\n{indent}{make_pointer}"
        return message


class YuiArray(object):
    """
    Yui言語の配列型

    Yui言語では、すべてのデータは配列として表現されます：
    - 文字列: 文字コードの配列
    - 数値: 桁の配列（浮動小数点数対応）
    - 配列: 要素の配列

    この統一的な表現により、すべてのデータを同じ方法で扱うことができます。

    Attributes:
        elements: 配列の要素リスト
        view: データの表示形式 ("string", "float", "array")

    Example:
        >>> arr = YuiArray("hello")  # 文字列を配列に
        >>> arr.elements  # [104, 101, 108, 108, 111] (文字コード)
        >>> arr.view  # "string"
    """
    elements: List[Any]
    view: str

    def __init__(self, values: Any):
        """
        YuiArrayを初期化する

        Args:
            values: 配列、文字列、または数値

        Raises:
            YuiError: サポートされていない型の場合
        """
        if isinstance(values, str):
            # 文字列は文字コードの配列として格納
            self.elements = [ord(ch) for ch in values]
            self.view = "string"
        elif isinstance(values, float):
            # 浮動小数点数は桁の配列として格納
            self.elements = YuiArray.float_to_digits(values)
            self.view = "float"
        elif isinstance(values, (list, tuple)):
            self.view = "array"
            # 配列の要素を再帰的にエンコード
            self.elements = [self.encode(v) for v in values]
        else:
            raise YuiError(f"文字列か配列を渡してください: ❌{values}")

    @classmethod
    def encode(cls, values):
        """
        Python値をYui言語の内部表現に変換する

        Args:
            values: 変換する値

        Returns:
            変換された値（YuiArrayまたはそのまま）
        """
        if isinstance(values, (list, str, float, tuple)):
            return YuiArray(values)
        if isinstance(values, dict):
            # 辞書の値を再帰的にエンコード
            for key, value in values.items():
                values[key] = YuiArray.encode(value)
            return values
        return values

    @classmethod
    def decode(cls, value: Any) -> Any:
        """
        Yui言語の内部表現をPython値に変換する

        Args:
            value: 変換する値

        Returns:
            変換された値（Python標準型）
        """
        if isinstance(value, YuiArray):
            if value.view == "string":
                # 文字コード配列を文字列に戻す
                chars = [chr(code) for code in value.elements]
                return ''.join(chars)
            if value.view == "float":
                # 桁配列を浮動小数点数に戻す
                return YuiArray.digits_to_float(value.elements)
            # 通常の配列は要素を再帰的にデコード
            return [YuiArray.decode(e) for e in value.elements]
        if isinstance(value, list):
            return [YuiArray.decode(e) for e in value]
        if isinstance(value, dict):
            new_value = {}
            for key, item in value.items():
                new_value[key] = YuiArray.decode(item)
            return new_value
        return value

    @classmethod
    def float_to_digits(cls, x: float) -> List[int]:
        """
        浮動小数点数を符号付き一桁整数配列に変換

        浮動小数点数を [sign, d1, d2, d3, ...] の形式に変換します。
        小数点以下4桁の精度で格納します。

        Args:
            x: 変換する浮動小数点数

        Returns:
            符号と桁のリスト [sign, d1, d2, ...]

        Example:
            >>> YuiArray.float_to_digits(3.14)
            [1, 3, 1, 4, 0, 0]  # 3.1400
            >>> YuiArray.float_to_digits(-2.5)
            [-1, 2, 5, 0, 0, 0]  # -2.5000
        """
        sign = -1 if x < 0 else 1
        s = f"{abs(x):.4f}"  # 小数点以下4桁に丸める
        s = s.replace('.', '')  # 小数点を削除
        digits = [sign] + [int(ch) for ch in s]
        return digits

    @classmethod
    def digits_to_float(cls, digits: List[int]) -> float:
        """
        符号付き一桁整数配列を浮動小数点数に変換

        float_to_digitsの逆変換を行います。

        Args:
            digits: [sign, d1, d2, ...] 形式の桁リスト

        Returns:
            浮動小数点数

        Example:
            >>> YuiArray.digits_to_float([1, 3, 1, 4, 0, 0])
            3.14
            >>> YuiArray.digits_to_float([-1, 2, 5, 0, 0, 0])
            -2.5
        """
        sign = digits[0]
        num_digits = digits[1:]
        s = ''.join(str(d) for d in num_digits)

        if len(s) <= 4:
            # 小数部のみの場合（整数部なし）
            value = int(s)
        else:
            # 小数点を4桁前に挿入
            value = float(s[:-4] + '.' + s[-4:])

        return sign * value

    def to_float(self) -> float:
        """
        この配列を浮動小数点数に変換する

        Returns:
            浮動小数点数

        Raises:
            YuiError: float viewでない場合
        """
        if self.view == "float":
            return YuiArray.digits_to_float(self.elements)
        raise YuiError(f"Floatに変換できません: ❌{self.elements}")

    def emit(self, lang="js", indent: str = "") -> str:
        """
        この配列をプログラムコードとして出力する

        Args:
            lang: 出力言語 ("js" or "py")
            indent: インデント文字列

        Returns:
            プログラムコードの文字列
        """
        if self.view == "string":
            # 文字列として出力
            chars = [chr(code) for code in self.elements]
            content = ''.join(chars).replace('\\', '\\\\').replace('\n', '\\n').replace('\t', '\\t').replace('"', '\\"')
            return '"' + content + '"'

        if self.view == "float":
            # 浮動小数点数として出力
            content = YuiArray.digits_to_float(self.elements)
            return f"{content:.4f}"

        if len(self.elements) == 0:
            return "[]"

        if isinstance(self.elements[0], YuiArray):
            # ネストした配列の場合、改行して整形
            lines = ["["]
            for element in self.elements:
                line = element.emit(lang, indent + "  ")
                lines.append(f"    {indent}{line},")
            lines[-1] = lines[-1][:-1]  # 最後のカンマを削除
            lines.append(f"{indent}]")
            return '\n'.join(lines)

        # 通常の配列
        elements = [str(element) for element in self.elements]
        return "[" + ", ".join(elements) + "]"

    def __str__(self):
        """文字列表現を返す"""
        return self.emit("js", "")

    def __repr__(self):
        """デバッグ用文字列表現を返す"""
        return self.emit("js", "")

    def __eq__(self, other):
        """等値比較"""
        if isinstance(other, YuiArray):
            return self.elements == other.elements
        return False



# =============================================================================
# セクション 2: 標準ライブラリ
# =============================================================================
# Yui言語の標準ライブラリ関数を定義します。
# これらの関数は「標準ライブラリを使う」で有効になります。
# =============================================================================

def to_number(v: Any) -> float:
    """
    値を数値に変換する

    Args:
        v: 変換する値

    Returns:
        数値

    Raises:
        YuiError: 数値に変換できない場合
    """
    if isinstance(v, (int, float)):
        return v
    if isinstance(v, YuiArray):
        return v.to_float()
    raise YuiError(f"数じゃないね: ❌{v}")

def compare(v: Any, v2: Any) -> int:
    """
    値を数値に変換する

    Args:
        v: 変換する値

    Returns:
        数値

    Raises:
        YuiError: 数値に変換できない場合
    """
    v = to_number(v)
    v2 = to_number(v2)
    if v < v2:
        return -1
    elif v > v2:
        return 1
    else:
        return 0

def standard_library(env: Dict[str, Any]):
    """
    標準ライブラリを環境に追加する

    以下の関数が使用可能になります：
    - 和(x): 要素の合計
    - 差(x): 要素の差
    - 積(x): 要素の積
    - 商(x): 要素の商
    - 剰余(x): 剰余
    - 絶対値(x): 絶対値
    - 最大値(x): 最大値
    - 最小値(x): 最小値
    - 配列化(x): 配列に変換
    - 文字列化(x): 文字列に変換
    - 乱数化(x): ランダムな整数

    Args:
        env: 関数を追加する環境
    """
    import random

    def yui_abs(*args: Any) -> Any:
        """絶対値を返す"""
        if len(args) != 1:
            raise YuiError(f"この関数の引数は1つだけだよ: ❌{args}")
        value = to_number(args[0])
        if isinstance(value, float) and not value.is_integer():
            return YuiArray(abs(value))
        return int(abs(value))

    def yui_sum(*args: Any) -> Any:
        """要素の合計を返す"""
        total = 0
        # 引数が配列1つの場合は、その要素を使う
        if len(args) == 1 and isinstance(args[0], YuiArray):
            args = args[0].elements
        for arg in args:
            total += to_number(arg)
        if isinstance(total, float) and not total.is_integer():
            return YuiArray(total)
        return int(total)

    def yui_sub(*args: Any) -> Any:
        """要素の差を返す"""
        if len(args) == 1 and isinstance(args[0], YuiArray):
            args = args[0].elements
        total = to_number(args[0])
        for arg in args[1:]:
            total -= to_number(arg)
        if isinstance(total, float) and not total.is_integer():
            return YuiArray(total)
        return int(total)

    def yui_accum(*args: Any) -> Any:
        """要素の積を返す"""
        if len(args) == 1 and isinstance(args[0], YuiArray):
            args = args[0].elements
        total = to_number(args[0])
        for arg in args[1:]:
            total *= to_number(arg)
        if isinstance(total, float) and not total.is_integer():
            return YuiArray(total)
        return int(total)

    def yui_div(*args: Any) -> Any:
        """要素の商を返す"""
        if len(args) == 1 and isinstance(args[0], YuiArray):
            args = args[0].elements
        total = to_number(args[0])
        for arg in args[1:]:
            total /= to_number(arg)
        if isinstance(total, float) and not total.is_integer():
            return YuiArray(total)
        return int(total)

    def yui_mod(*args: Any) -> Any:
        """剰余を返す"""
        if len(args) == 1 and isinstance(args[0], YuiArray):
            args = args[0].elements
        total = to_number(args[0])
        for arg in args[1:]:
            total %= to_number(arg)
        if isinstance(total, float) and not total.is_integer():
            return YuiArray(total)
        return int(total)

    def yui_max(*args: Any) -> Any:
        """最大値を返す"""
        if len(args) == 1 and isinstance(args[0], YuiArray):
            args = args[0].elements
        result = max(to_number(arg) for arg in args)
        if isinstance(result, float) and not result.is_integer():
            return YuiArray(result)
        return int(result)

    def yui_min(*args: Any) -> Any:
        """最小値を返す"""
        if len(args) == 1 and isinstance(args[0], YuiArray):
            args = args[0].elements
        result = min(to_number(arg) for arg in args)
        if isinstance(result, float) and not result.is_integer():
            return YuiArray(result)
        return int(result)

    def yui_toint(*args: Any) -> Any:
        """整数に変換する"""
        if len(args) != 1:
            raise YuiError(f"引数は1つだけだよ: ❌{args}")
        value = int(to_number(args[0]))
        return value

    def yui_round(*args: Any) -> Any:
        """整数に変換する"""
        if len(args) != 1:
            raise YuiError(f"引数は1つだけだよ: ❌{args}")
        return int(round(to_number(args[0]), 0))

    def yui_todecimal(*args: Any) -> Any:
        """小数に変換する"""
        if len(args) != 1:
            raise YuiError(f"引数は1つだけだよ: ❌{args}")
        value = float(to_number(args[0]))
        return YuiArray(value)

    def yui_toarray(*args: Any) -> Any:
        """配列に変換する"""
        if len(args) != 1:
            raise YuiError(f"引数は1つだけだよ: ❌{args}")
        if isinstance(args[0], YuiArray):
            args[0].view = "array"
        raise YuiError(f"配列に変換できません: ❌{args[0]}")

    def yui_tostring(*args: Any) -> Any:
        """文字列に変換する"""
        if len(args) != 1:
            raise YuiError(f"引数は1つだけだよ: ❌{args}")
        if isinstance(args[0], YuiArray):
            if args[0].view == "float":
                return YuiArray(f"{args[0].to_float}")
            args[0].is_string_view = True
            return args[0]
        if isinstance(args[0], int):
            return YuiArray(int(args[0]))
        raise YuiError(f"文字列に変換できません: ❌{args[0]}")

    def yui_random(*args: Any) -> Any:
        """ランダムな整数を返す"""
        if len(args) == 0:
            return YuiArray(random.random())
        if len(args) != 1:
            raise YuiError(f"引数は1つだけだよ: ❌{args}")
        if isinstance(args[0], int):
            return random.randint(0, args[0] - 1)
        raise YuiError(f"整数を渡してね: ❌{args[0]}")

    # 環境に関数を登録
    env["和"] = FunctionNode(["x"], yui_sum)
    env["差"] = FunctionNode(["x"], yui_sub)
    env["積"] = FunctionNode(["x"], yui_accum)
    env["商"] = FunctionNode(["x"], yui_div)
    env["剰余"] = FunctionNode(["x"], yui_mod)
    env["絶対値"] = FunctionNode(["x"], yui_abs)
    env["最大値"] = FunctionNode(["x"], yui_max)
    env["最小値"] = FunctionNode(["x"], yui_min)
    env["整数化"] = FunctionNode(["x"], yui_toint)
    env["四捨五入"] = FunctionNode(["x"], yui_round)
    env["少数化"] = FunctionNode(["x"], yui_todecimal)
    env["配列化"] = FunctionNode(["x"], yui_toarray)
    env["文字列化"] = FunctionNode(["x"], yui_tostring)
    env["乱数生成"] = FunctionNode(["x"], yui_random)

def arithmetic_library(env: Dict[str, Any]):
    """
    算術ライブラリを環境に追加する

    以下の三角関数が使用可能になります：
    - sin(x): サイン
    - cos(x): コサイン
    - tan(x): タンジェント

    Args:
        env: 関数を追加する環境
    """
    import math

    def yui_sin(x: Any) -> Any:
        """サインを返す"""
        value = to_number(x)
        result = math.sin(value)
        return YuiArray(result)

    def yui_cos(x: Any) -> Any:
        """コサインを返す"""
        value = to_number(x)
        result = math.cos(value)
        return YuiArray(result)

    def yui_tan(x: Any) -> Any:
        """タンジェントを返す"""
        value = to_number(x)
        result = math.tan(value)
        return YuiArray(result)

    env["sin"] = FunctionNode(["x"], yui_sin)
    env["cos"] = FunctionNode(["x"], yui_cos)
    env["tan"] = FunctionNode(["x"], yui_tan)


# =============================================================================
# セクション 3: ランタイム環境
# =============================================================================
# Yui言語のプログラム実行環境を定義します。
# - Environment: 変数と関数のスコープを管理
# - YuiRuntime: プログラムの実行を制御
# =============================================================================

class Environment(dict):
    """
    Yui言語の実行環境（変数のスコープ）

    Pythonの辞書を拡張し、変数の読み書きを管理します。
    また、ランタイムへの参照を持ち、実行状態の追跡を行います。

    Attributes:
        runtime: このEnvironmentが属するYuiRuntime
        readonly_names: 読み取り専用の変数名リスト
    """
    runtime: 'YuiRuntime'
    readonly_names: List[str]

    def __init__(self, runtime: 'YuiRuntime', parent: Optional['Environment'] = None):
        """
        Environmentを初期化する

        Args:
            runtime: このEnvironmentが属するYuiRuntime
            parent: 親Environment（関数呼び出し時に使用）
        """
        self.runtime = runtime
        if parent is not None:
            # 親Environmentの変数をコピー
            for key, value in parent.items():
                self[key] = YuiArray.encode(value)
            self.readonly_names = list(parent.keys())
        else:
            self.readonly_names = []

    def diff(self, old_env: Dict[str, Any]) -> Dict[str, Any]:
        """
        環境の差分を返す（新しく追加または変更された変数）

        Args:
            old_env: 比較元の環境

        Returns:
            差分の辞書
        """
        new_env = {}
        for key, value in self.items():
            if key not in old_env or old_env[key] != value:
                new_env[key] = value
        return new_env

    def push_call_frame(self, func_name: str, args: List[Any], pos: int):
        """関数呼び出しフレームをスタックに追加"""
        self.runtime.call_frames.append((func_name, args, pos))

    def pop_call_frame(self):
        """関数呼び出しフレームをスタックから削除"""
        self.runtime.call_frames.pop()

    def count_inc(self):
        """インクリメント操作のカウントを増やす"""
        self.runtime.increment_count += 1

    def count_dec(self):
        """デクリメント操作のカウントを増やす"""
        self.runtime.decrement_count += 1

    def count_compare(self):
        """比較操作のカウントを増やす"""
        self.runtime.compare_count += 1

    def print(self, value: Any, pos: int):
        """値を出力する"""
        self.runtime.print(value, pos)

    def update_variable(self, name: str, value: Any, pos: int):
        """変数を更新する"""
        self.runtime.update_variable(name, value, pos)

    def check_execution(self, code_map: tuple):
        """実行状態をチェック（タイムアウトなど）"""
        self.runtime.check_execution(code_map, self)

    def check_recursion_depth(self):
        """再帰呼び出しの深さをチェック"""
        if len(self.runtime.call_frames) > 512:
            args = ", ".join(str(arg) for arg in self.runtime.call_frames[-1][1])
            snippet = f"{self.runtime.call_frames[-1][0]}({args})"
            raise YuiError(f"再帰呼び出しが深さが上限(=512)を超えました: 最後の呼び出し 🔍{snippet}")


class YuiRuntime(object):
    """
    Yui言語のランタイムシステム

    プログラムの実行を制御し、以下の機能を提供します：
    - プログラムのパースと実行
    - タイムアウト制御
    - 実行統計の収集（インクリメント、デクリメント、比較の回数）
    - 再帰呼び出しの追跡

    Attributes:
        source: 実行中のソースコード
        increment_count: インクリメント操作の回数
        decrement_count: デクリメント操作の回数
        compare_count: 比較操作の回数
        call_frames: 関数呼び出しスタック
        shouldStop: 手動停止フラグ
        timeout: タイムアウト時間（秒）
        interactive_mode: インタラクティブモードフラグ
    """
    increment_count: int
    decrement_count: int
    compare_count: int
    call_frames: List[tuple]  # (func_name, args, pos)

    def __init__(self):
        """YuiRuntimeを初期化する"""
        self.source = ""
        self.increment_count = 0
        self.decrement_count = 0
        self.compare_count = 0
        self.call_frames = []
        self.shouldStop = False
        self.timeout = 0
        self.interactive_mode = False

    def exec(self, source: str, env: Environment = None, timeout: int = 30,
             eval_mode: bool = False):
        """
        Yuiプログラムを実行する

        Args:
            source: Yuiプログラムのソースコード
            env: 実行環境（省略時は新規作成）
            timeout: タイムアウト時間（秒）
            eval_mode: 式評価モード（環境ではなく値を返す）

        Returns:
            eval_mode=True: 評価結果の値
            eval_mode=False: 実行後の環境

        Example:
            >>> runtime = YuiRuntime()
            >>> result = runtime.exec("x = 10", eval_mode=False)
            >>> result['x']
            10
        """
        self.source = source

        # 環境の準備
        if not isinstance(env, Environment):
            env = Environment(self, env)

        # パースして実行
        parser = YuiParser()
        program = parser.parse(source)
        self.start(timeout)
        value = program.evaluate(env)

        # 結果を返す
        return YuiArray.decode(value) if eval_mode else env

    def load(self, function: FunctionType, parameters: List[str]):
        """Python関数をYui関数として読み込む"""
        return FunctionNode(parameters, function)

    def update_variable(self, name: str, env: Dict[str, Any], pos: int):
        """変数更新時のフック（サブクラスでオーバーライド可能）"""
        pass

    def print(self, value: Any, pos: int):
        """
        値を出力する

        Args:
            value: 出力する値
            pos: ソースコード内の位置
        """
        _, line, col, snipet = parse_error(self.source, pos)
        if self.interactive_mode:
            print(f"{value}")
        else:
            print(f">>> {snipet.strip()}   #({line}行目)\n{value}")

    def start(self, timeout: int = 30):
        """実行を開始する"""
        self.shouldStop = False
        self.timeout = timeout
        self.startTime = time.time()

    def check_execution(self, code_map: tuple, env: Environment):
        """
        実行状態をチェックする

        手動停止フラグとタイムアウトをチェックし、
        必要に応じてYuiErrorを発生させます。

        Args:
            code_map: エラー位置情報
            env: 現在の環境

        Raises:
            YuiError: 手動停止またはタイムアウト時
        """
        # 手動停止フラグのチェック
        if self.shouldStop:
            raise YuiError('プログラムが手動で停止されました', code_map, env)

        # タイムアウトチェック
        if self.timeout > 0 and (time.time() - self.startTime) > self.timeout:
            raise YuiError(f'タイムアウト({self.timeout}秒)になりました', code_map, env)

    def stringfy_as_json(self, env: Dict[str, Any]) -> str:
        """
        環境をJSON形式の文字列として出力する

        Args:
            env: 出力する環境

        Returns:
            JSON形式の文字列
        """
        env = YuiArray.encode(env)
        lines = ["{"]
        indent = "    "

        for key, value in env.items():
            key_str = f"{indent}\"{key}\":"
            if isinstance(value, (int, float)):
                lines.append(f"{key_str} {int(value)},")
            if isinstance(value, YuiArray):
                content = value.emit("js", indent)
                lines.append(f"{key_str} {content},")
            if value is None:
                lines.append(f"{key_str} null,")

        if len(lines) > 1:
            lines[-1] = lines[-1][:-1]  # 最後のカンマを削除
        lines.append("}")
        return '\n'.join(lines)


# =============================================================================
# セクション 4: AST (抽象構文木) ノード
# =============================================================================
# Yuiプログラムの構造を表現するノードクラスを定義します。
# すべてのノードはASTNodeを継承し、evaluateとemitメソッドを実装します。
# =============================================================================

@dataclass
class ASTNode(ABC):
    """
    抽象構文木（AST）の基底クラス

    すべてのASTノードはこのクラスを継承します。
    各ノードはソースコード内の位置情報を持ち、
    評価（evaluate）とコード生成（emit）ができます。

    Attributes:
        source: ソースコード
        pos: ノードの開始位置
        end_pos: ノードの終了位置
    """
    source: str
    pos: int
    end_pos: int

    def __init__(self):
        """ASTNodeを初期化する"""
        self.source = ""
        self.pos = 0
        self.end_pos = 0

    def code_map(self) -> tuple:
        """ノードの位置情報を返す"""
        return self.source, self.pos, self.end_pos

    @abstractmethod
    def evaluate(self, env: Environment) -> Any:
        """
        ノードを評価する

        Args:
            env: 評価環境

        Returns:
            評価結果
        """
        pass

    @abstractmethod
    def emit(self, lang: str = "js", indent: str = "") -> str:
        """
        ノードをコードとして出力する

        Args:
            lang: 出力言語 ("js" or "py")
            indent: インデント文字列

        Returns:
            プログラムコードの文字列
        """
        pass

    def semicolon(self, lang: str = "js") -> str:
        """言語に応じたセミコロンを返す"""
        if lang == "py":
            return ""
        return ";"


@dataclass
class StatementNode(ASTNode):
    """
    文（Statement）の基底クラス

    代入、ループ、条件分岐など、プログラムの実行可能な文を表現します。
    """
    def __init__(self):
        super().__init__()


@dataclass
class ExpressionNode(ASTNode):
    """
    式（Expression）の基底クラス

    数値、文字列、変数、関数呼び出しなど、値を返す式を表現します。
    """
    def __init__(self):
        super().__init__()


@dataclass
class ProgramNode(StatementNode):
    """
    プログラム全体を表すノード

    複数の文のリストとして表現されます。

    Attributes:
        statements: 文のリスト
    """
    statements: List[StatementNode]

    def __init__(self, statements: List[StatementNode]):
        super().__init__()
        self.statements = statements

    def evaluate(self, env: Environment):
        """プログラム内のすべての文を順に評価する"""
        value = env
        for statement in self.statements:
            value = statement.evaluate(env)
        return value

    def emit(self, lang: str = "js", indent: str = "") -> str:
        """プログラムをコードとして出力する"""
        lines = []
        for statement in self.statements:
            lines.append(statement.emit(lang, indent))
        return "\n".join(lines)


@dataclass
class BlockNode(StatementNode):
    """
    ブロック（{ }で囲まれた文の集まり）を表すノード

    関数本体、ループ本体、条件分岐の本体などに使用されます。

    Attributes:
        statements: ブロック内の文のリスト
    """
    statements: List[StatementNode]

    def __init__(self, statements: List[StatementNode]):
        super().__init__()
        self.statements = statements

    def evaluate(self, env: Environment):
        """ブロック内のすべての文を順に評価する"""
        for statement in self.statements:
            statement.evaluate(env)

    def emit(self, lang: str = "js", indent: str = "") -> str:
        """ブロックをコードとして出力する"""
        lines = []
        for statement in self.statements:
            lines.append(statement.emit(lang, indent + "    "))

        if lang == "py":
            if len(lines) == 0:
                lines.append(f"{indent}pass")
        else:
            lines.append(f"{indent}}}")

        return "\n".join(lines)


@dataclass
class NullNode(ExpressionNode):
    """
    null値（?）を表すノード
    """
    def __init__(self):
        super().__init__()

    def evaluate(self, env: Environment):
        """None を返す"""
        return None

    def emit(self, lang: str = "js", indent: str = "") -> str:
        """null/None を出力する"""
        if lang == "py":
            return "None"
        return "null"


@dataclass
class NumberNode(ExpressionNode):
    """
    数値リテラルを表すノード

    整数および浮動小数点数をサポートします。

    Attributes:
        value: 数値
    """
    value: Union[int, float]

    def __init__(self, value: Union[int, float]):
        super().__init__()
        self.value = value

    def evaluate(self, env: Environment):
        """数値を返す（浮動小数点数はYuiArrayに変換）"""
        if isinstance(self.value, float):
            return YuiArray(self.value)
        return self.value

    def emit(self, lang: str = "js", indent: str = "") -> str:
        """数値を文字列として出力する"""
        return str(self.value)


@dataclass
class ArrayLenNode(ExpressionNode):
    """
    配列の長さ（|配列|）を表すノード

    | | で囲まれた式の長さを返します。

    Attributes:
        element: 長さを取得する式
    """
    element: ExpressionNode

    def __init__(self, element: ExpressionNode):
        super().__init__()
        self.element = element

    def evaluate(self, env: Environment):
        """配列の長さを返す"""
        value = self.element.evaluate(env)
        if isinstance(value, YuiArray):
            return len(value.elements)
        raise YuiError(f"配列じゃないね？ ❌{value}", self.element.code_map(), env)

    def emit(self, lang: str = "js", indent: str = "") -> str:
        """length/len() を出力する"""
        if lang == "py":
            return "len(" + self.element.emit(lang, indent) + ")"
        return "(" + self.element.emit(lang, indent) + ").length"


@dataclass
class MinusNode(ExpressionNode):
    """
    負の数（-式）を表すノード

    Attributes:
        element: 符号を反転する式
    """
    element: ExpressionNode

    def __init__(self, element: ExpressionNode):
        super().__init__()
        self.element = element

    def evaluate(self, env: Environment):
        """式を評価して符号を反転する"""
        value = self.element.evaluate(env)
        value = to_number(value)
        if isinstance(value, float):
            return YuiArray(-value)
        return -value

    def emit(self, lang: str = "js", indent: str = "") -> str:
        """-式 を出力する"""
        return f"-{self.element.emit(lang, indent)}"


@dataclass
class ArrayNode(ExpressionNode):
    """
    配列リテラル（[要素, ...]）を表すノード

    Attributes:
        elements: 配列の要素のリスト
    """
    elements: List[Any]

    def __init__(self, elements: List[Any]):
        super().__init__()
        self.elements = elements

    def evaluate(self, env: Environment):
        """各要素を評価してYuiArrayを作成する"""
        array_content = [element.evaluate(env) for element in self.elements]
        return YuiArray(array_content)

    def emit(self, lang: str = "js", indent: str = "") -> str:
        """配列リテラルを出力する"""
        elements = []
        for element in self.elements:
            elements.append(element.emit(lang, indent))
        return "[" + ", ".join(elements) + "]"


@dataclass
class StringNode(ExpressionNode):
    """
    文字列リテラル（"..."）を表すノード

    文字列はYuiArrayとして格納されます。

    Attributes:
        value: YuiArray形式の文字列
    """
    value: List[Any]

    def __init__(self, content: str):
        super().__init__()
        self.value = YuiArray(content)

    def evaluate(self, env: Environment):
        """YuiArrayを返す"""
        return self.value

    def emit(self, lang: str = "js", indent: str = "") -> str:
        """文字列リテラルを出力する"""
        return self.value.emit(lang, indent)


@dataclass
class FunctionNode(ExpressionNode):
    """
    関数定義を表すノード

    Yui言語の関数は、パラメータリストと本体（ブロックまたはPython関数）から成ります。

    Attributes:
        name: 関数名
        parameters: パラメータ名のリスト
        body: 関数本体（BlockNodeまたはPython関数）
    """
    name: str
    parameters: List[str]
    body: Union[BlockNode, FunctionType]

    def __init__(self, parameters: List[str], body: Union[BlockNode, FunctionType]):
        super().__init__()
        self.parameters = parameters
        self.body = body

        # 関数名の設定
        if self.is_native():
            self.name = f"<function:{self.body.__name__}>"
        else:
            self.name = "<lambda>"

    def is_native(self) -> bool:
        """ネイティブ（Python）関数かどうかを返す"""
        return not isinstance(self.body, BlockNode)

    def evaluate(self, env: Environment):
        """自分自身を返す（関数は第一級オブジェクト）"""
        return self

    def emit(self, lang: str = "js", indent: str = "") -> str:
        """関数定義を出力する"""
        params = ", ".join(self.parameters)
        body = self.body.emit(lang, indent)
        if lang == "py":
            return f"def {self.name}({params}):\n{body}"
        return f"function ({params}) {{\n{body}"


@dataclass
class FuncCallNode(ExpressionNode):
    """
    関数呼び出し（関数名(引数, ...)）を表すノード

    Attributes:
        name: 関数名
        arguments: 引数のリスト
    """
    name: str
    arguments: List[ExpressionNode]

    def __init__(self, name: str, arguments: List[ExpressionNode]):
        super().__init__()
        self.name = name
        self.arguments = arguments

    def evaluate(self, env: Environment):
        """
        関数を呼び出して結果を返す

        ネイティブ関数の場合は直接Python関数を呼び出し、
        Yui関数の場合は新しい環境を作成して本体を評価します。
        """
        # 関数の存在チェック
        if not self.name in env:
            if self.name in ['和', '配列化', '文字列化']:
                raise YuiError(f"最初に「標準ライブラリを使う」と宣言して！", self.code_map(), env)
            raise YuiError(f"関数定義を忘れていない？: ❌{self.name}", self.code_map(), env)

        function = env[self.name]
        if not isinstance(function, FunctionNode):
            raise YuiError(f"{self.name}は関数ではありません: ❌{self.function}", self.code_map(), env)

        # ネイティブ関数の呼び出し
        if function.is_native():
            arguments = [argument.evaluate(env) for argument in self.arguments]
            try:
                return function.body(*arguments)
            except YuiError as e:
                e.update_code_map(self.code_map(), env)
                raise e
            except Exception as e:
                raise YuiError(f"{self.name}関数の実行中にエラーが発生しました: {e}", self.code_map(), env)

        # Yui関数の呼び出し
        # パラメータ数のチェック
        if len(function.parameters) != len(self.arguments):
            raise YuiError(f"この関数の引数は{len(function.parameters)}つだよ: ❌{self.arguments}", self.code_map(), env)

        # 新しい環境を作成
        new_env: Environment = Environment(env.runtime, env)
        arguments = []
        for parameter, argument in zip(function.parameters, self.arguments):
            value = argument.evaluate(env)
            new_env[parameter] = value
            arguments.append(value)

        try:
            # 関数本体を評価
            new_env.push_call_frame(self.name, arguments, self.pos)
            new_env.check_recursion_depth()
            function.body.evaluate(new_env)
        except YuiReturnException as e:
            # return 文で値が返された
            new_env.pop_call_frame()
            return e.value
        except YuiError as e:
            e.update_code_map(self.code_map(), env)
            raise e

        # return 文がない場合は変更された変数のみ返す
        new_env.pop_call_frame()
        return new_env.diff(env)

    def emit(self, lang: str = "js", indent: str = "") -> str:
        """関数呼び出しを出力する"""
        arguments = []
        for argument in self.arguments:
            arguments.append(argument.emit(lang, indent))
        params = ", ".join(arguments)
        return f"{self.name}({params})"


# ヘルパー関数
def check_name(name: str, code_map: tuple, env: Environment) -> Any:
    """変数が定義されているかチェックし、値を返す"""
    if name not in env:
        raise YuiError(f"知らない変数だよ！ ❌'{name}'", code_map, env)
    return env[name]


def check_int(value: Any, code_map: tuple, env: Environment) -> int:
    """値が整数に変換可能かチェックし、整数を返す"""
    if isinstance(value, (int, float)):
        return int(value)
    raise YuiError(f"整数ではありません: ❌{value}", code_map, env)


def check_array(array: Any, code_map: tuple, env: Environment) -> YuiArray:
    """値が配列かチェックし、YuiArrayを返す"""
    if not isinstance(array, YuiArray):
        raise YuiError(f"配列ではありません: ❌{array}", code_map, env)
    return array


def check_array_index(array: YuiArray, index_value: int, code_map: tuple,
                      env: Environment) -> int:
    """配列のインデックスが有効範囲かチェックし、整数インデックスを返す"""
    if isinstance(index_value, (int, float)):
        index_value = int(index_value)
        if 0 <= index_value < len(array.elements):
            return index_value
    if len(array.elements) == 0:
        raise YuiError(f"配列は空です。添え字の確認も: ❌{index_value}", code_map, env)
    raise YuiError(f"配列の添え字は0から{len(array.elements)-1}の間ですよ: ❌{index_value}", code_map, env)


@dataclass
class VariableNode(ExpressionNode):
    """
    変数参照（変数名[インデックス]...）を表すノード

    単純な変数参照だけでなく、配列の要素アクセスもサポートします。

    Attributes:
        name: 変数名
        indices: インデックスのリスト（配列アクセス用）
    """
    name: str
    indices: List[ExpressionNode]

    def __init__(self, name: str, indices: Optional[List[ExpressionNode]] = None):
        super().__init__()
        self.name = name
        self.indices = indices

    def evaluate(self, env: Environment):
        """変数の値を返す（インデックスがあれば配列要素を返す）"""
        value = check_name(self.name, self.code_map(), env)

        # インデックスがない場合は変数の値をそのまま返す
        if self.indices is None or len(self.indices) == 0:
            return value

        # インデックスがある場合は配列要素にアクセス
        for index in self.indices:
            array = check_array(value, self.code_map(), env)
            index_value = check_array_index(array, index.evaluate(env), index.code_map(), env)
            value = array.elements[index_value]
        return value

    def evaluate_with_update(self, env: Environment, updated_value):
        """
        変数を更新する（代入用）

        インデックスがある場合は配列要素を更新します。

        Args:
            env: 環境
            updated_value: 新しい値
        """
        if self.indices is None or len(self.indices) == 0:
            # 単純な変数への代入
            env[self.name] = updated_value
            return

        # 配列要素への代入
        value = check_name(self.name, self.code_map(), env)
        for i, index in enumerate(self.indices):
            array = check_array(value, self.code_map(), env)
            index_value = check_array_index(array, index.evaluate(env), index.code_map(), env)
            if i == len(self.indices) - 1:
                # 最後のインデックス：値を更新
                array.elements[index_value] = updated_value
            else:
                # 中間のインデックス：次の配列に進む
                value = array.elements[index_value]

    def emit(self, lang: str = "js", indent: str = "") -> str:
        """変数参照を出力する"""
        if self.indices is None or len(self.indices) == 0:
            return self.name

        indices = []
        for index in self.indices:
            indices.append(f"[{index.emit(lang, indent)}]")
        indices_str = "".join(indices)
        return f"{self.name}{indices_str}"


@dataclass
class AssignmentNode(StatementNode):
    """
    代入文（変数 = 式）を表すノード

    Attributes:
        variable: 代入先の変数
        expression: 代入する式
    """
    variable: VariableNode
    expression: ExpressionNode

    def __init__(self, variable: VariableNode, expression: ExpressionNode):
        super().__init__()
        self.variable = variable
        self.expression = expression

        # 関数を代入する場合は関数名を設定
        if isinstance(expression, FunctionNode):
            expression.name = variable.name

    def evaluate(self, env: Environment):
        """式を評価して変数に代入する"""
        value = self.expression.evaluate(env)
        env.update_variable(self.variable.name, value, self.pos)
        self.variable.evaluate_with_update(env, value)

    def emit(self, lang: str = "js", indent: str = "") -> str:
        """代入文を出力する"""
        variable = self.variable.emit(lang, indent)
        expression = self.expression.emit(lang, indent)

        # Python の関数定義は特別な構文
        if lang == "py" and isinstance(self.expression, FunctionNode):
            return f"{indent}{expression}"

        return f"{indent}{variable} = {expression}{self.semicolon(lang)}"


@dataclass
class AppendNode(StatementNode):
    """
    配列への追加（変数の末尾に 値 を 追加する）を表すノード

    Attributes:
        variable: 追加先の配列
        expression: 追加する値
    """
    variable: VariableNode
    expression: ExpressionNode

    def __init__(self, variable: VariableNode, expression: ExpressionNode):
        super().__init__()
        self.variable = variable
        self.expression = expression

    def evaluate(self, env: Environment):
        """値を評価して配列に追加する"""
        array = check_array(self.variable.evaluate(env), self.variable.code_map(), env)
        value = self.expression.evaluate(env)
        array.elements.append(value)

    def emit(self, lang: str = "js", indent: str = "") -> str:
        """配列への追加を出力する"""
        variable = self.variable.emit(lang, indent)
        expression = self.expression.emit(lang, indent)

        if lang == "py":
            return f'{indent}{variable}.append({expression})'
        if lang == "js":
            return f'{indent}{variable}.push({expression}){self.semicolon(lang)}'
        return f'{indent}{variable}.append({expression})'


@dataclass
class IncrementNode(StatementNode):
    """
    インクリメント（変数 を 増やす）を表すノード

    Attributes:
        variable: インクリメントする変数
    """
    variable: VariableNode

    def __init__(self, variable: VariableNode):
        super().__init__()
        self.variable = variable

    def evaluate(self, env: Environment):
        """変数を1増やす"""
        value = self.variable.evaluate(env)
        value = check_int(value, self.variable.code_map(), env)
        self.variable.evaluate_with_update(env, value + 1)
        env.count_inc()

    def emit(self, lang: str = "js", indent: str = "") -> str:
        """インクリメントを出力する"""
        variable = self.variable.emit(lang, indent)
        return f"{indent}{variable} += 1{self.semicolon(lang)}"


@dataclass
class DecrementNode(StatementNode):
    """
    デクリメント（変数 を 減らす）を表すノード

    Attributes:
        variable: デクリメントする変数
    """
    variable: VariableNode

    def __init__(self, variable: VariableNode):
        super().__init__()
        self.variable = variable

    def evaluate(self, env: Environment):
        """変数を1減らす"""
        value = self.variable.evaluate(env)
        value = check_int(value, self.variable.code_map(), env)
        self.variable.evaluate_with_update(env, value - 1)
        env.count_dec()

    def emit(self, lang: str = "js", indent: str = "") -> str:
        """デクリメントを出力する"""
        variable = self.variable.emit(lang, indent)
        return f"{indent}{variable} -= 1{self.semicolon(lang)}"


@dataclass
class IfNode(StatementNode):
    """
    条件分岐（もし〜ならば）を表すノード

    Attributes:
        left: 左辺の式
        operator: 比較演算子
        right: 右辺の式
        then_block: 条件が真の時のブロック
        else_block: 条件が偽の時のブロック（オプション）
    """
    left: ExpressionNode
    operator: str  # "以上", "以下", "より大きい", "より小さい", "以外", "未満", ""
    right: ExpressionNode
    then_block: BlockNode
    else_block: Optional[BlockNode] = None

    def __init__(self, left: ExpressionNode, operator: str, right: ExpressionNode,
                 then_block: BlockNode, else_block: Optional[BlockNode] = None):
        super().__init__()
        self.left = left
        self.operator = operator
        self.right = right
        self.then_block = then_block
        self.else_block = else_block

    def evaluate(self, env: Environment):
        """条件を評価して適切なブロックを実行する"""
        left_value = self.left.evaluate(env)
        right_value = self.right.evaluate(env)

        # 演算子に応じて比較
        if self.operator == "以上":
            result = compare(left_value, right_value) >= 0
        elif self.operator == "以下":
            result = compare(left_value, right_value) <= 0
        elif self.operator == "より大きい":
            result = compare(left_value, right_value) > 0
        elif self.operator == "より小さい":
            result = compare(left_value, right_value) < 0
        elif self.operator == "以外":
            result = compare(left_value, right_value) != 0
        elif self.operator == "未満":
            raise YuiError("`未満`の代わりに`より小さい`を使ってね", self.right.code_map(), env)
        else:
            result = compare(left_value, right_value) == 0

        env.count_compare()

        # 結果に応じてブロックを実行
        if result:
            self.then_block.evaluate(env)
        elif self.else_block:
            self.else_block.evaluate(env)

    def emit(self, lang: str = "js", indent: str = "") -> str:
        """条件分岐を出力する"""
        left = self.left.emit(lang, indent)
        right = self.right.emit(lang, indent)

        # 演算子を変換
        if self.operator == "以上":
            op = ">="
        elif self.operator == "以下":
            op = "<="
        elif self.operator == "より大きい":
            op = ">"
        elif self.operator == "より小さい":
            op = "<"
        elif self.operator == "以外":
            op = "!="
        else:
            op = "=="

        lines = []
        if lang == "py":
            lines.append(f"{indent}if {left} {op} {right}:")
        else:
            lines.append(f"{indent}if({left} {op} {right}) {{")

        lines.append(self.then_block.emit(lang, indent))

        if self.else_block:
            if lang == "py":
                lines.append(f"{indent}else:")
            else:
                lines.append(f"{indent}else {{")
            lines.append(self.else_block.emit(lang, indent))

        return "\n".join(lines)


def check_loop_count(value: Any, code_map: tuple, env: Environment) -> int:
    """
    ループ回数が有効かチェックし、整数を返す

    Args:
        value: チェックする値
        code_map: エラー位置情報
        env: 環境

    Returns:
        ループ回数（整数）

    Raises:
        YuiError: 無効な値の場合
    """
    if isinstance(value, YuiArray):
        raise YuiError(f"`| |`で囲んでみようか？: ❌{value}", code_map, env)
    if isinstance(value, (int, float)):
        count = int(value)
        if count >= 0:
            return count
    raise YuiError(f"くり返しは0回以上の整数で: ❌{value}", code_map, env)


# =============================================================================
# ループと制御フロー
# =============================================================================

class YuiBreakException(RuntimeError):
    """ループを抜けるための例外"""
    def __init__(self):
        pass


@dataclass
class BreakNode(StatementNode):
    """
    ループ脱出（くり返しを抜ける）を表すノード
    """
    def __init__(self):
        super().__init__()

    def evaluate(self, env: Environment):
        """YuiBreakExceptionを発生させる"""
        raise YuiBreakException()

    def emit(self, lang: str = "js", indent: str = "") -> str:
        """break文を出力する"""
        return f"{indent}break{self.semicolon(lang)}"


@dataclass
class LoopNode(StatementNode):
    """
    ループ（N回 くり返す）を表すノード

    Attributes:
        count: ループ回数（NullNodeの場合は無限ループ）
        body: ループ本体
    """
    count: ExpressionNode
    body: BlockNode

    def __init__(self, count: ExpressionNode, body: BlockNode):
        super().__init__()
        self.count = count
        self.body = body

    def evaluate(self, env: Environment):
        """ループを実行する"""
        loop_count = self.count.evaluate(env)
        code_map = self.count.code_map()

        # 無限ループ（? 回 くり返す）
        if loop_count is None:
            try:
                while True:
                    env.check_execution(code_map)
                    self.body.evaluate(env)
            except YuiBreakException:
                pass
            return

        # 有限ループ（N 回 くり返す）
        loop_count = check_loop_count(loop_count, code_map, env)
        try:
            for _ in range(int(loop_count)):
                env.check_execution(code_map)
                self.body.evaluate(env)
        except YuiBreakException:
            pass

    def emit(self, lang: str = "js", indent: str = "") -> str:
        """ループを出力する"""
        lines = []

        if isinstance(self.count, NullNode):
            # 無限ループ
            if lang == "py":
                lines.append(f"{indent}while True:")
            else:
                lines.append(f"{indent}while(true) {{")
        else:
            # 有限ループ
            count = self.count.emit(lang, indent)
            if lang == "py":
                lines.append(f"{indent}for _ in range({count}):")
            else:
                i = f"i{len(indent)//4}"
                lines.append(f"{indent}for(var {i} = 0; {i} < {count}; {i}++) {{")

        lines.append(self.body.emit(lang, indent))
        return "\n".join(lines)


@dataclass
class ImportNode(StatementNode):
    """
    ライブラリのインポート（標準ライブラリを使う）を表すノード

    Attributes:
        module_name: ライブラリ名
    """
    module_name: str

    def __init__(self, module_name: str):
        super().__init__()
        self.module_name = module_name

    def evaluate(self, env: Environment):
        """ライブラリを環境に追加する"""
        runtime: YuiRuntime = env.runtime
        if self.module_name == "標準":
            standard_library(env)
        elif self.module_name == "算術":
            arithmetic_library(env)
        else:
            raise YuiError(f"'{self.module_name}'ライブラリの名前はOKですか？", self.code_map(), env)

    def emit(self, lang: str = "js", indent: str = "") -> str:
        """何も出力しない（インポートは実行時処理）"""
        return f"{indent}"


class YuiReturnException(RuntimeError):
    """関数から値を返すための例外"""
    def __init__(self, value=None):
        self.value = value


@dataclass
class ReturnNode(StatementNode):
    """
    関数からの返値（式 が 答え）を表すノード

    Attributes:
        expression: 返す値の式
    """
    expression: ExpressionNode

    def __init__(self, expression: ExpressionNode):
        super().__init__()
        self.expression = expression

    def evaluate(self, env: Environment):
        """式を評価してYuiReturnExceptionを発生させる"""
        value = self.expression.evaluate(env)
        raise YuiReturnException(value)

    def emit(self, lang: str = "js", indent: str = "") -> str:
        """return文を出力する"""
        return f"{indent}return {self.expression.emit(lang, indent)}{self.semicolon(lang)}"


@dataclass
class PrintExpressionNode(StatementNode):
    """
    式の出力（単独で書かれた式）を表すノード

    Attributes:
        expression: 出力する式
    """
    expression: ExpressionNode

    def __init__(self, expression: ExpressionNode):
        super().__init__()
        self.expression = expression

    def evaluate(self, env: Environment):
        """式を評価して結果を出力する"""
        value = self.expression.evaluate(env)
        env.runtime.print(value, self.expression.pos)
        return value

    def emit(self, lang: str = "js", indent: str = "") -> str:
        """式を出力する"""
        return f"{indent}{self.expression.emit(lang, indent)}{self.semicolon(lang)}"


@dataclass
class TestNode(StatementNode):
    """
    テストケース（>>> 式 → 期待値）を表すノード

    Attributes:
        expression: テストする式
        answer: 期待される値
    """
    expression: ExpressionNode
    answer: ExpressionNode

    def __init__(self, expression: ExpressionNode, answer: ExpressionNode):
        super().__init__()
        self.expression = expression
        self.answer = answer

    def evaluate(self, env: Environment):
        """式を評価して期待値と比較する"""
        value = self.expression.evaluate(env)
        answer_value = self.answer.evaluate(env)
        if value != answer_value:
            raise YuiError(f"テストに失敗: ❌{value}\n(正解) {answer_value}", self.code_map(), env)

    def emit(self, lang: str = "js", indent: str = "") -> str:
        """アサーション文を出力する"""
        expression = self.expression.emit(lang, indent)
        answer = self.answer.emit(lang, indent)

        if lang == "js":
            return f"{indent}console.assert({expression} == {answer}){self.semicolon(lang)}"
        return f"{indent}assert ({expression} == {answer}){self.semicolon(lang)}"


# =============================================================================
# セクション 5: パーサー
# =============================================================================
# Yuiプログラムのソースコードを解析してASTを構築します。
# =============================================================================

class YuiParser(object):
    """
    Yui言語のパーサー

    ソースコードを字句解析・構文解析してASTを構築します。
    再帰下降パーサーとして実装されています。

    Attributes:
        text: パース中のテキスト
        pos: 現在の解析位置
        length: テキストの長さ
        in_function: 関数定義内かどうか
        in_loop: ループ内かどうか
        variables: 定義された変数のリスト
    """
    text: str
    pos: int
    length: int
    in_function: bool
    in_loop: bool
    variables: List[str]

    def __init__(self):
        """YuiParserを初期化する"""
        self.init_text("")
        self.in_function = False
        self.in_loop = False
        self.variables = []

    def init_text(self, text: str, reset_variables: bool = True):
        """
        パース対象のテキストを設定する

        Args:
            text: パースするテキスト
            reset_variables: 変数リストをリセットするか
        """
        self.text = self.normalize(text)
        self.pos = 0
        self.length = len(text)
        if reset_variables:
            self.variables = []

    def normalize(self, text: str) -> str:
        """
        全角文字を半角に変換する

        全角の英数字と引用符を半角に正規化します。
        これにより、ユーザーが全角で入力しても正しく解析できます。

        Args:
            text: 正規化するテキスト

        Returns:
            正規化されたテキスト
        """
        # スマートクォートと全角ダブルクォートを半角に変換
        text = text.replace('"', '"').replace('"', '"').replace('＂', '"')

        # 全角英数字を半角に変換（範囲指定は機能しないため個別に列挙）
        zenkaku = '０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'
        hankaku = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        return text.translate(str.maketrans(zenkaku, hankaku))

    def add_variable(self, name: str):
        """
        変数リストに変数名を追加する

        長い変数名を優先するため、長さの降順でソートします。

        Args:
            name: 追加する変数名
        """
        if name not in self.variables:
            self.variables.append(name)
        self.variables.sort(key=lambda x: -len(x))

    def parse(self, text: str) -> ProgramNode:
        """
        テキストをパースしてASTを返す

        Args:
            text: パースするYuiプログラム

        Returns:
            ProgramNode: プログラム全体を表すAST
        """
        self.init_text(text)
        return self.parse_program()

    def code_map(self, start_pos: Optional[int] = None) -> tuple:
        """
        現在の位置情報を返す

        Args:
            start_pos: 開始位置（省略時は現在位置）

        Returns:
            (text, start_pos, current_pos)のタプル
        """
        if start_pos is None:
            start_pos = self.pos
        return (self.text, start_pos, self.pos)

    def parse_program(self) -> ProgramNode:
        """
        プログラム全体をパースする

        Returns:
            ProgramNode: プログラム全体を表すAST
        """
        statements = []
        self.consume_whitespace(include_newline=True)

        while self.pos < self.length:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.consume_whitespace(include_newline=True)

        return ProgramNode(statements)

    def parse_statement(self, text=None) -> Optional[StatementNode]:
        """
        1つの文をパースする

        Args:
            text: パースするテキスト（省略時は現在のテキスト）

        Returns:
            StatementNode: パースされた文のAST

        Raises:
            YuiError: 構文エラーの場合
        """
        if text is not None:
            self.init_text(text)

        self.consume_whitespace(include_newline=True)
        saved_pos = self.pos

        # 各種文を試みる
        stmt = self.parse_IfNode()
        if not stmt:
            stmt = self.LoopNode()
        if not stmt:
            stmt = self.parse_TestNode()
        if not stmt:
            stmt = self.parse_AssignmentNode()
        if not stmt:
            stmt = self.parse_ReturnNode()
        if not stmt:
            stmt = self.parse_BreakNode()
        if not stmt:
            stmt = self.parse_ImportNode()

        if stmt:
            # 位置情報を設定
            stmt.source = self.text
            stmt.pos = saved_pos
            stmt.end_pos = self.pos
            self.consume_whitespace(include_newline=True)
            return stmt

        # どの構文にもマッチしない
        raise YuiError(f"ゆいの知らない書き方だね！", self.code_map(saved_pos))

    def parse_TestNode(self) -> StatementNode:
        """テストケース（>>> 式 → 期待値）をパースする"""
        saved_pos = self.pos
        if not self.consume_string(">>>"):
            self.pos = saved_pos
            return None

        self.consume_whitespace()
        expression = self.parse_expression()
        if expression is None:
            raise YuiError(f"`>>>` の後にはテストする式が必要です", self.code_map(saved_pos))

        self.consume_eol()
        answer_expression = self.parse_expression()
        if answer_expression is None:
            raise YuiError(f"`>>>` の次の行には正解が必要です", self.code_map(saved_pos))

        return TestNode(expression, answer_expression)

    def parse_AssignmentNode(self) -> AssignmentNode:
        """
        代入文をパースする

        以下の構文をサポート：
        - 変数 = 式
        - 変数 を 増やす
        - 変数 を 減らす
        - 変数の末尾に 値 を 追加する
        """
        saved_pos = self.pos

        # 変数名をパース
        variable: VariableNode = self.parse_VariableNode(definition_context=True)
        if variable is None:
            self.pos = saved_pos
            return None

        self.consume_whitespace()

        # 配列への追加
        if self.consume("の末尾に"):
            self.consume_comma()
            expression = self.parse_expression()
            if expression is None:
                raise YuiError(f"ここに何か忘れてません？", self.code_map(saved_pos))
            self.consume_whitespace()
            self.consume_string("を")
            self.consume_comma()
            self.consume("追加する", "ついかする")
            return AppendNode(variable, expression)

        # インクリメント・デクリメント
        if self.consume_string("を"):
            self.consume_whitespace()
            if self.consume("増やす", "ふやす"):
                return IncrementNode(variable)
            if self.consume("減らす", "へらす"):
                return DecrementNode(variable)
            raise YuiError(f"`増やす`か`減らす`かどちら？", self.code_map(saved_pos))

        # 通常の代入
        if self.consume("=", "＝"):
            self.consume_whitespace()
            expression = self.parse_expression()
            if expression is None:
                raise YuiError(f"ここに何か忘れてません？", self.code_map(saved_pos))

            self.add_variable(variable.name)
            return AssignmentNode(variable, expression)

        # エラーメッセージ
        if self.consume("に") and self.find("追加する", "ついかする") != -1:
            raise YuiError(f"`の末尾に`をつけてね", self.code_map(saved_pos))

        end_pos = self.find("=", "＝", "を増やす", "を減らす")
        if end_pos != -1:
            bad_name = self.text[saved_pos:end_pos-1].strip()
            raise YuiError(f"変数名`{bad_name}`を別に変えてみて", self.code_map(saved_pos))

        self.pos = saved_pos
        return None

    def parse_IfNode(self) -> IfNode:
        """
        条件分岐（もし〜ならば）をパースする

        構文: もし A が B [演算子] ならば { ... } [そうでなければ { ... }]
        """
        saved_pos = self.pos

        if not self.consume_string("もし"):
            self.pos = saved_pos
            return None
        self.consume_comma()

        # 左辺
        if self.consume("ならば", "が", "のとき", "の場合"):
            raise YuiError(f"何と比較したいの？", self.code_map())

        left = self.parse_expression()
        if not left:
            raise YuiError(f"何と比較したいの？", self.code_map())

        if not self.consume_string("が"):
            raise YuiError(f"`が`が必要", self.code_map())

        self.consume_comma()

        # 右辺
        if self.consume("ならば", "のとき", "の場合"):
            raise YuiError(f"何と比較したいの？", self.code_map())

        right = self.parse_expression()
        if not right:
            raise YuiError(f"何と比較したいの？", self.code_map())
        self.consume_whitespace()

        # 比較演算子
        operator = ""
        for op in ["以上", "以下", "より大きい", "より小さい", "以外"]:
            if self.consume_string(op):
                operator = op
                break
        self.consume_whitespace()

        if self.consume("未満"):
            raise YuiError("`未満`の代わりに`より小さい`を使ってね", self.code_map())

        if not self.consume_string("ならば"):
            raise YuiError("`ならば`が必要", self.code_map())
        self.consume_comma()

        # then ブロック
        then_block = self.parse_block()
        if then_block is None:
            raise YuiError("「もし〜ならば」どうするの？ { }で囲んで書いてね！", self.code_map())

        # else ブロック（オプション）
        else_block = self.parse_else_statement()
        return IfNode(left, operator, right, then_block, else_block)

    def parse_else_statement(self) -> BlockNode:
        """else節（そうでなければ）をパースする"""
        saved_pos = self.pos
        self.consume_whitespace(include_newline=True)
        if not self.consume_string("そうでなければ"):
            self.pos = saved_pos
            return None
        self.consume_comma()
        block = self.parse_block()
        if block is None:
            raise YuiError("「そうでなければ」どうするの？ { }で囲んで書いてね！", self.code_map())
        return block

    def LoopNode(self) -> LoopNode:
        """
        ループ（N回 くり返す）をパースする

        構文: N回 くり返す { ... }
        """
        saved_pos = self.pos
        count = self.parse_expression()
        if count is None:
            self.pos = saved_pos
            return None
        if not self.consume_string("回"):
            self.pos = saved_pos
            return None
        self.consume_comma()
        if not self.consume("くり返す", "繰り返す"):
            raise YuiError(f"`くり返す`が必要", self.code_map(saved_pos))

        # ループ本体をパース
        saved_in_loop = self.in_loop
        self.in_loop = True
        body = self.parse_block()
        self.in_loop = saved_in_loop

        if body is None:
            raise YuiError("何をくり返すの？ { }で囲んで書いてね！", self.code_map(saved_pos))
        return LoopNode(count, body)

    def parse_ReturnNode(self) -> ReturnNode:
        """返値（式 が 答え）または式の出力をパースする"""
        saved_pos = self.pos
        expression = self.parse_expression()
        if expression:
            # 「が 答え」で終わる場合はreturn文
            if self.consume("が") and self.consume("答え", "こたえ"):
                if not self.in_function:
                    raise YuiError("関数定義{ }の内側で使うものだよ", self.code_map())
                return ReturnNode(expression)

            # 単独の式は出力
            self.consume_whitespace()
            if self.pos >= self.length or self.text[self.pos] == '\n':
                return PrintExpressionNode(expression)

        self.pos = saved_pos
        return None

    def parse_BreakNode(self) -> BreakNode:
        """ループ脱出（くり返しを抜ける）をパースする"""
        saved_pos = self.pos
        if not self.consume("くり返し", "繰り返し", "くりかえし"):
            self.pos = saved_pos
            return None
        if self.consume("から"):
            raise YuiError("「くり返し`を`抜ける」です", self.code_map())
        if self.consume("を") and self.consume("抜ける", "ぬける"):
            if not self.in_loop:
                raise YuiError("くり返し{ }の内側で使うものだよ", self.code_map())
            return BreakNode()
        self.pos = saved_pos
        return None

    def parse_ImportNode(self) -> ImportNode:
        """ライブラリのインポート（ライブラリを使う）をパースする"""
        saved_pos = self.pos
        if self.consume("標準") and self.consume("ライブラリを使う"):
            return ImportNode("標準")
        if self.consume("算術") and self.consume("ライブラリを使う"):
            return ImportNode("算術")
        libname = self.parse_endswith("ライブラリを使う")
        if libname:
            return ImportNode(libname)
        self.pos = saved_pos
        return None

    def parse_endswith(self, suffix: str) -> bool:
        """行が指定の接尾辞で終わるかチェックする"""
        pos = self.pos
        while pos < self.length:
            char = self.text[pos]
            if char in "#＃\r\n":
                break
            pos += 1
        line = self.text[self.pos:pos].strip()
        if line.endswith(suffix):
            substring = line[:-len(suffix)]
            self.pos += len(substring) + len(suffix)
            return substring.strip()
        return None

    def parse_expression(self, text=None) -> ExpressionNode:
        """
        式をパースする

        各種リテラルや演算子を試みます。
        """
        if text is not None:
            self.init_text(text, reset_variables=False)

        self.consume_whitespace()
        saved_pos = self.pos

        # 各種式を試みる
        expression = self.parse_NumberNode()
        if not expression:
            expression = self.parse_StringNode()
        if not expression:
            expression = self.parse_ArrayLenNode()
        if not expression:
            expression = self.parse_MinusNode()
        if not expression:
            expression = self.parse_FunctionNode()
        if not expression:
            expression = self.parse_ArrayNode()
        if not expression:
            expression = self.parse_NullNode()
        if not expression:
            expression = self.parse_FuncCallNode()
        if not expression:
            expression = self.parse_VariableNode()

        if expression:
            # 中置演算子のエラーチェック
            if self.consume("+", "-", "*", "/", "%", "＋", "ー", "＊", "／", "％", "×", "÷"):
                raise YuiError("ゆいは中置記法を使えないよ！", self.code_map())

            # 位置情報を設定
            expression.source = self.text
            expression.pos = saved_pos
            expression.end_pos = self.pos
            self.consume_whitespace()
            return expression

        return None

    def parse_NumberNode(self) -> NumberNode:
        """数値リテラルをパースする"""
        saved_pos = self.pos
        if not self.consume_digit():
            self.pos = saved_pos
            return None

        # 整数部
        while self.consume_digit():
            pass

        # 小数部
        if self.consume("."):
            if not self.consume_digit():
                raise YuiError(f"`.`の後に数字が必要", self.code_map())
            while self.consume_digit():
                pass

            # 小数点数
            value_str = self.text[saved_pos:self.pos]
            try:
                value = float(value_str)
                if value < 0.0001:
                    raise YuiError(f"0.0001がゆいの最小精度だよ！", self.code_map(saved_pos))
                return NumberNode(value)
            except ValueError:
                raise YuiError(f"数値の書き方がおかしい", self.code_map(saved_pos))
        else:
            # 整数
            value_str = self.text[saved_pos:self.pos]
            try:
                value = int(value_str)
                return NumberNode(value)
            except ValueError:
                raise YuiError(f"数値の書き方がおかしい", self.code_map(saved_pos))

    def parse_StringNode(self) -> StringNode:
        """文字列リテラル（"..."）をパースする"""
        saved_pos = self.pos

        # ダブルクォート開始
        if not self.consume('"', """, """):
            self.pos = saved_pos
            return None

        # 文字列内容を読み取り
        string_content = []
        while self.pos < self.length and self.text[self.pos] != '"':
            char = self.text[self.pos]
            if char == '\\' and self.pos + 1 < self.length:
                # エスケープシーケンスの処理
                self.pos += 1
                next_char = self.text[self.pos]
                if next_char == 'n':
                    string_content.append('\n')
                elif next_char == 't':
                    string_content.append('\t')
                elif next_char == '\\':
                    string_content.append('\\')
                elif next_char == '"':
                    string_content.append('"')
                else:
                    string_content.append(next_char)
            else:
                string_content.append(char)
            self.pos += 1

        # ダブルクォート終了
        if not self.consume('"', """, """):
            self.pos = saved_pos
            raise YuiError(f"閉じ`\"`を忘れないで", self.code_map(saved_pos))

        # 文字コードを取り出す（"hello"[0]）
        if self.consume("[", "【", "［"):
            self.consume_whitespace()
            saved_pos = self.pos
            number = self.parse_NumberNode()
            if number is None:
                raise YuiError(f"添え字を忘れているよ", self.code_map(saved_pos))
            self.consume_whitespace()
            if not self.consume("]", "】", "］"):
                raise YuiError(f"閉じ`]`を忘れないで", self.code_map(saved_pos))
            if len(string_content) == 0:
                raise YuiError(f"空の文字列に添え字は使えません", self.code_map(saved_pos))
            if not (0 <= int(number.value) < len(string_content)):
                raise YuiError(f"添え字は0から{len(string_content)-1}の間ですよ: ❌{number.value}", self.code_map(saved_pos))
            return NumberNode(ord(string_content[int(number.value)]))

        return StringNode(''.join(string_content))

    def parse_MinusNode(self) -> MinusNode:
        """負の数（-式）をパースする"""
        saved_pos = self.pos

        if not self.consume("-", "ー"):
            self.pos = saved_pos
            return None
        self.consume_whitespace()
        element = self.parse_expression()
        if element is None:
            raise YuiError(f"`-`の次に何か忘れてない？", self.code_map())
        return MinusNode(element)

    def parse_ArrayLenNode(self) -> ArrayLenNode:
        """配列の長さ（|配列|）をパースする"""
        saved_pos = self.pos
        if not self.consume("|", "｜"):
            self.pos = saved_pos
            return None

        self.consume_whitespace()
        element = self.parse_expression()
        if element is None:
            raise YuiError(f"`|`の次に何か忘れてない？", self.code_map())
        self.consume_whitespace()
        if not self.consume("|", "｜"):
            raise YuiError(f"閉じ`|`を忘れないで", self.code_map(saved_pos))
        return ArrayLenNode(element)

    def parse_FunctionNode(self) -> FunctionNode:
        """
        関数定義をパースする

        構文: 入力 x, y に対して { ... }
        """
        saved_pos = self.pos
        if not self.consume("入力", "λ"):
            self.pos = saved_pos
            return None

        self.consume_whitespace()

        # パラメータ
        parameters = []
        while True:
            name_pos = self.pos
            name = self.parse_name(definition_context=True)
            if name is None:
                raise YuiError(f"関数定義には引数が必要", self.code_map(name_pos))
            if name in parameters:
                raise YuiError(f"同じ引数名を使っているよ: ❌'{name}'", self.code_map(name_pos))
            parameters.append(name)
            self.consume_whitespace()
            if not self.consume(",", "、", "，", "､"):
                break
            self.consume_whitespace()

        if len(parameters) == 0:
            raise YuiError(f"ひとつは引数名が必要", self.code_map(saved_pos))

        self.consume_whitespace()
        if not self.consume_string("に対し"):
            raise YuiError(f"`に対し`が必要", self.code_map(saved_pos))
        self.consume_string("て")
        self.consume_comma()

        # 関数本体をパース
        saved_variables = self.variables.copy()
        saved_in_function = self.in_function
        self.in_function = True
        self.variables = self.variables + parameters
        body = self.parse_block()
        self.variables = saved_variables
        self.in_function = saved_in_function

        if body is None:
            raise YuiError("関数定義の本体は？ { }で囲んで書いてね！", self.code_map(saved_pos))
        return FunctionNode(parameters, body)

    def parse_FuncCallNode(self) -> FuncCallNode:
        """関数呼び出し（関数名(引数, ...)）をパースする"""
        saved_pos = self.pos
        name = self.parse_name()
        if name is None:
            self.pos = saved_pos
            return None
        self.consume_whitespace()

        if not self.consume("(", "（"):
            self.pos = saved_pos
            return None

        self.consume_whitespace()

        # 引数リスト
        arguments = []
        while True:
            local_pos = self.pos
            expression = self.parse_expression()
            if expression is None:
                raise YuiError(f"引数を忘れないで", self.code_map(local_pos))
            arguments.append(expression)
            self.consume_whitespace()
            if self.consume(")", "）"):
                break
            if not self.consume(",", "、", "，", "､"):
                raise YuiError(f"閉じ`)`を忘れないで", self.code_map())
            self.consume_whitespace(include_newline=True)

        return FuncCallNode(name, arguments)

    def parse_ArrayNode(self) -> ArrayNode:
        """配列リテラル（[要素, ...]）をパースする"""
        saved_pos = self.pos
        if not self.consume("[", "［"):
            self.pos = saved_pos
            return None

        elements = []
        saved_pos = self.pos
        while True:
            self.consume_whitespace(include_newline=True)
            if self.consume("]", "］"):
                break
            head_pos = self.pos
            expression = self.parse_expression()
            if expression is None:
                raise YuiError(f"配列の要素か、閉じ`]`を忘れてない？", self.code_map(head_pos))
            elements.append(expression)
            self.consume_whitespace(include_newline=True)
            if self.consume("]", "］"):
                break
            if not self.consume(",", "、", "，", "､"):
                raise YuiError(f"閉じ`]`を忘れないで", self.code_map(saved_pos))

        return ArrayNode(elements)

    def parse_NullNode(self) -> NullNode:
        """null値（?）をパースする"""
        if self.consume("?", "？"):
            return NullNode()
        return None

    def parse_VariableNode(self, definition_context=False) -> VariableNode:
        """変数参照（変数名[インデックス]...）をパースする"""
        saved_pos = self.pos
        name = self.parse_name(definition_context=definition_context)
        if name is None:
            self.pos = saved_pos
            return None

        # 配列インデックス
        indices = []
        while self.consume("[", "［"):
            self.consume_whitespace()
            index = self.parse_expression()
            if index is None:
                raise YuiError(f"添え字を忘れているよ", self.code_map())
            indices.append(index)
            if not self.consume("]", "］"):
                raise YuiError(f"閉じ `]`を忘れないで", self.code_map())

        if len(indices) == 0:
            indices = None

        v = VariableNode(name, indices)
        v.source = self.text
        v.pos = saved_pos
        v.end_pos = self.pos
        return v

    def parse_block(self) -> BlockNode:
        """ブロック（{ ... }）をパースする"""
        self.consume_whitespace()
        saved_pos = self.pos
        if not self.consume("{", "｛"):
            self.pos = saved_pos
            return None

        open_pos = self.pos
        self.consume_until_eol()
        self.consume_whitespace()

        found_closing_brace = False
        statements = []
        while self.pos < self.length:
            self.consume_whitespace(include_newline=True)
            if self.consume("}", "｝"):
                found_closing_brace = True
                break
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)

        if not found_closing_brace:
            raise YuiError("閉じ `}`を忘れないで", self.code_map(open_pos-1))

        return BlockNode(statements)

    def parse_name(self, definition_context: bool = False) -> str:
        """
        識別子（変数名・関数名）をパースする

        Args:
            definition_context: 定義コンテキスト（より寛容なパース）

        Returns:
            識別子の文字列、またはNone
        """
        saved_pos = self.pos

        if definition_context:
            # 定義コンテキスト：区切り文字まで読む
            while self.pos < self.length:
                char = self.text[self.pos]
                if char in " \t\n\r,=[](){}#　＝＃、，､【】［］（）｛｝":
                    break
                if char in "にをの":
                    remaining = self.text[self.pos:]
                    if remaining.startswith("に対し") or remaining.startswith("を増やす") or \
                       remaining.startswith("を減らす") or remaining.startswith("の末尾に"):
                        break
                self.pos += 1
            name = self.text[saved_pos:self.pos].strip()
            if len(name) > 0:
                return name
            return None

        # 参照コンテキスト：既知の変数または英数字識別子
        if self.consume(*self.variables):
            return self.text[saved_pos:self.pos]
        elif not self.consume_alpha():
            self.pos = saved_pos
            return None

        while (not self.is_keywords()) and self.consume_alpha():
            pass

        while self.consume_digit():
            pass

        name = self.text[saved_pos:self.pos]
        if len(name) > 0:
            return name
        return None

    def is_keywords(self) -> bool:
        """現在位置がキーワードの始まりかチェックする"""
        remaining = self.text[self.pos:]
        for kw in ["を", "とする", "が", "ならば", "に対し", "の末尾に", "を増やす"]:
            if remaining.startswith(kw):
                return True
        return False

    def consume_alpha(self) -> bool:
        """英字・日本語文字を1文字消費する"""
        if self.pos < self.length:
            char = self.text[self.pos]
            if (char.isalpha() or char == '_' or
                    '\u4e00' <= char <= '\u9fff' or  # 漢字
                    '\u3040' <= char <= '\u309f' or  # ひらがな
                    '\u30a0' <= char <= '\u30ff' or  # カタカナ
                    char == 'ー'):
                self.pos += 1
                return True
        return False

    def consume_string(self, string: str) -> bool:
        """指定した文字列を消費する"""
        if self.text[self.pos:].startswith(string):
            self.pos += len(string)
            return True
        return False

    def consume(self, *strings) -> bool:
        """いずれかの文字列を消費する"""
        for string in strings:
            if self.consume_string(string):
                return True
        return False

    def find(self, *substrings: str) -> int:
        """いずれかの部分文字列が最初に見つかる位置を返す"""
        saved_pos = self.pos
        while self.pos < self.length:
            char = self.text[self.pos]
            if self.consume(*substrings):
                found_pos = self.pos
                self.pos = saved_pos
                return found_pos
            if char in "#＃\r\n":
                break
            self.pos += 1
        self.pos = saved_pos
        return -1

    def consume_digit(self) -> bool:
        """数字を1文字消費する"""
        if self.pos >= self.length:
            return False
        if self.text[self.pos].isdigit():
            self.pos += 1
            return True
        return False

    def consume_whitespace(self, include_newline: bool = False):
        """空白文字を消費する"""
        c = 0
        while self.pos < self.length:
            if self.text[self.pos] in " 　\t\r":
                self.pos += 1
                c += 1
                continue
            if include_newline and self.text[self.pos] in '#＃':
                self.consume_until_eol()
                c = 0
                continue
            if include_newline and self.text[self.pos] == '\n':
                self.pos += 1
                c = 0
            else:
                break
        return c

    def consume_comma(self, include_newline: bool = False):
        """読点を消費する"""
        self.consume("、", "，", ",", "､")
        self.consume_whitespace(include_newline)

    def consume_eol(self):
        """行末を消費する"""
        self.consume_whitespace()
        if self.pos < self.length and self.text[self.pos] == '\n':
            self.pos += 1
        elif self.pos >= self.length:
            pass  # ファイル終端
        else:
            # EOLが見つからない場合でもエラーにしない
            pass

    def consume_until_eol(self):
        """改行まで読み飛ばす"""
        while self.pos < self.length and self.text[self.pos] != '\n':
            self.pos += 1
        if self.pos < self.length:
            self.pos += 1
