# bigdecimalstring.py
from __future__ import annotations

import re
from dataclasses import dataclass
# THIS FILE IS PART OF: "NoLimits" PYTHON LIBRARY
@dataclass(frozen=True)
class BigDecimal:
    # Normalized representation:
    # - sign: +1 or -1
    # - digits: string of decimal digits without leading zeros (except "0")
    # - scale: number of fractional digits (>= 0)
    sign: int
    digits: str
    scale: int

    # ------------- Construction -------------

    @staticmethod
    def from_string(s: str) -> "BigDecimal":
        s = s.strip().replace("_", "")
        if not s:
            raise ValueError("empty string")

        # Match optional sign, digits, optional fractional part
        m = re.match(r'^([+-])?(\d+)(?:\.(\d+))?$', s)
        if not m:
            raise ValueError(f"invalid decimal: {s}")

        sign_str, int_part, frac_part = m.groups()
        sign = -1 if sign_str == '-' else 1
        frac_part = frac_part or ""

        # Remove leading zeros from integer part
        int_part = int_part.lstrip('0')
        if int_part == "":
            int_part = "0"

        digits = int_part + frac_part
        scale = len(frac_part)

        # Normalize zeros
        if BigDecimal._is_all_zeros(digits):
            return BigDecimal(1, "0", 0)

        # Strip trailing zeros in fractional portion by reducing scale
        digits, scale = BigDecimal._strip_trailing_fractional_zeros(digits, scale)

        # Remove leading zeros
        digits = BigDecimal._strip_leading_zeros(digits)

        return BigDecimal(sign, digits, scale)

    @staticmethod
    def zero() -> "BigDecimal":
        return BigDecimal(1, "0", 0)

    @staticmethod
    def one() -> "BigDecimal":
        return BigDecimal(1, "1", 0)

    # ------------- Formatting -------------

    def __str__(self) -> str:
        if self.digits == "0":
            return "0"
        # Insert decimal point according to scale
        if self.scale == 0:
            s = self.digits
        else:
            n = len(self.digits)
            if self.scale >= n:
                # pad with leading zeros
                int_part = "0"
                frac_pad = "0" * (self.scale - n)
                frac_part = frac_pad + self.digits
            else:
                int_part = self.digits[: n - self.scale]
                frac_part = self.digits[n - self.scale :]
            # remove trailing zeros in fractional part for display
            frac_part = frac_part.rstrip('0')
            if frac_part == "":
                s = int_part
            else:
                s = f"{int_part}.{frac_part}"

        return s if self.sign > 0 else f"-{s}"

    def to_tuple(self) -> tuple[int, str, int]:
        return (self.sign, self.digits, self.scale)

    # ------------- Comparisons -------------

    def _cmp_mag(self, other: "BigDecimal") -> int:
        a_digits, a_scale = self.digits, self.scale
        b_digits, b_scale = other.digits, other.scale
        # Align scales (pad with trailing zeros)
        if a_scale < b_scale:
            a_digits += "0" * (b_scale - a_scale)
        elif b_scale < a_scale:
            b_digits += "0" * (a_scale - b_scale)
        # Compare lengths then lexicographically
        if len(a_digits) < len(b_digits):
            return -1
        if len(a_digits) > len(b_digits):
            return 1
        if a_digits < b_digits:
            return -1
        if a_digits > b_digits:
            return 1
        return 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BigDecimal):
            return False
        # Normalize zeros
        a = self.normalize()
        b = other.normalize()
        return a.sign == b.sign and a.digits == b.digits and a.scale == b.scale

    def __lt__(self, other: "BigDecimal") -> bool:
        if self.sign != other.sign:
            return self.sign < other.sign
        if self.sign > 0:
            return self._cmp_mag(other) < 0
        else:
            return self._cmp_mag(other) > 0

    def __le__(self, other: "BigDecimal") -> bool:
        return self == other or self < other

    def __gt__(self, other: "BigDecimal") -> bool:
        return not self <= other

    def __ge__(self, other: "BigDecimal") -> bool:
        return not self < other

    # ------------- Normalization utilities -------------

    def normalize(self) -> "BigDecimal":
        if self.digits == "0":
            return BigDecimal.zero()
        digits, scale = self.digits, self.scale
        digits, scale = BigDecimal._strip_trailing_fractional_zeros(digits, scale)
        digits = BigDecimal._strip_leading_zeros(digits)
        if digits == "":
            return BigDecimal.zero()
        return BigDecimal(self.sign, digits, scale)

    @staticmethod
    def _strip_leading_zeros(d: str) -> str:
        d2 = d.lstrip('0')
        return d2 if d2 != "" else "0"

    @staticmethod
    def _strip_trailing_fractional_zeros(d: str, scale: int) -> tuple[str, int]:
        if scale == 0:
            return (d, scale)
        # Remove trailing zeros only from fractional part boundary
        # We can remove up to scale trailing zeros
        remove = 0
        i = len(d) - 1
        while remove < scale and i >= 0 and d[i] == '0':
            remove += 1
            i -= 1
        if remove > 0:
            d = d[: len(d) - remove]
            scale -= remove
        return (d if d != "" else "0", scale)

    @staticmethod
    def _is_all_zeros(d: str) -> bool:
        return all(c == '0' for c in d)

    # ------------- Scale alignment -------------

    @staticmethod
    def _align(a: "BigDecimal", b: "BigDecimal") -> tuple[str, str, int]:
        # returns (A_digits_aligned, B_digits_aligned, common_scale)
        if a.scale == b.scale:
            return (a.digits, b.digits, a.scale)
        if a.scale < b.scale:
            pad = b.scale - a.scale
            return (a.digits + "0" * pad, b.digits, b.scale)
        else:
            pad = a.scale - b.scale
            return (a.digits, b.digits + "0" * pad, a.scale)

    # ------------- Addition/Subtraction -------------

    def __neg__(self) -> "BigDecimal":
        if self.digits == "0":
            return self
        return BigDecimal(-self.sign, self.digits, self.scale)

    def __add__(self, other: "BigDecimal") -> "BigDecimal":
        a = self.normalize()
        b = other.normalize()
        if a.digits == "0":
            return b
        if b.digits == "0":
            return a
        if a.sign == b.sign:
            ad, bd, sc = BigDecimal._align(a, b)
            sum_digits = BigDecimal._add_digits(ad, bd)
            return BigDecimal(a.sign, sum_digits, sc).normalize()
        else:
            # a + (-b) == a - b
            ad, bd, sc = BigDecimal._align(a, b)
            cmp = BigDecimal._cmp_digits(ad, bd)
            if cmp == 0:
                return BigDecimal.zero()
            if cmp > 0:
                diff = BigDecimal._sub_digits(ad, bd)
                return BigDecimal(a.sign, diff, sc).normalize()
            else:
                diff = BigDecimal._sub_digits(bd, ad)
                return BigDecimal(b.sign, diff, sc).normalize()

    def __sub__(self, other: "BigDecimal") -> "BigDecimal":
        return self + (-other)

    @staticmethod
    def _add_digits(a: str, b: str) -> str:
        # a, b are digit strings, no sign, same "scale alignment" already handled
        i, j = len(a) - 1, len(b) - 1
        carry = 0
        out = []
        while i >= 0 or j >= 0 or carry:
            da = ord(a[i]) - 48 if i >= 0 else 0
            db = ord(b[j]) - 48 if j >= 0 else 0
            s = da + db + carry
            out.append(chr(48 + (s % 10)))
            carry = s // 10
            i -= 1
            j -= 1
        return "".join(reversed(out))

    @staticmethod
    def _cmp_digits(a: str, b: str) -> int:
        # Compare by length then lexicographically
        if len(a) != len(b):
            return -1 if len(a) < len(b) else 1
        if a == b:
            return 0
        return -1 if a < b else 1

    @staticmethod
    def _sub_digits(a: str, b: str) -> str:
        # Compute a - b where a >= b, return digit string
        i, j = len(a) - 1, len(b) - 1
        borrow = 0
        out = []
        while i >= 0:
            da = ord(a[i]) - 48
            db = ord(b[j]) - 48 if j >= 0 else 0
            v = da - borrow - db
            if v < 0:
                v += 10
                borrow = 1
            else:
                borrow = 0
            out.append(chr(48 + v))
            i -= 1
            j -= 1
        # strip leading zeros
        res = "".join(reversed(out)).lstrip('0')
        return res if res != "" else "0"

    # ------------- Multiplication -------------

    def __mul__(self, other: "BigDecimal") -> "BigDecimal":
        a = self.normalize()
        b = other.normalize()
        if a.digits == "0" or b.digits == "0":
            return BigDecimal.zero()
        prod_digits = BigDecimal._mul_digits(a.digits, b.digits)
        scale = a.scale + b.scale
        sign = a.sign * b.sign
        return BigDecimal(sign, prod_digits, scale).normalize()

    @staticmethod
    def _mul_digits(a: str, b: str) -> str:
        # Grade-school multiplication
        n, m = len(a), len(b)
        res = [0] * (n + m)
        for i in range(n - 1, -1, -1):
            ai = ord(a[i]) - 48
            carry = 0
            for j in range(m - 1, -1, -1):
                bj = ord(b[j]) - 48
                k = i + j + 1
                s = ai * bj + res[k] + carry
                res[k] = s % 10
                carry = s // 10
            res[i] += carry
        # convert to string, strip leading zeros
        out = "".join(chr(48 + d) for d in res).lstrip('0')
        return out if out != "" else "0"

    # ------------- Division (fixed precision) -------------

    def div(self, other: "BigDecimal", prec: int) -> "BigDecimal":
        """
        Divide self by other, producing 'prec' fractional digits.
        Result is rounded down (truncation).
        """
        a = self.normalize()
        b = other.normalize()
        if b.digits == "0":
            raise ZeroDivisionError("division by zero")
        if a.digits == "0":
            return BigDecimal.zero()

        # Align to integers by scaling both so divisor becomes integer
        # Let’s produce integer division on big integers:
        # shift = max(a.scale, b.scale)
        # But to get fractional digits, we will scale numerator further by 'prec'
        # Steps:
        # 1) Make both integers: A = a.digits * 10^(S - a.scale), B = b.digits * 10^(S - b.scale)
        #    where S = max(a.scale, b.scale)
        # 2) Produce quotient with extra 'prec' digits: Q = (A * 10^prec) // B
        # 3) Set result scale = prec
        S = max(a.scale, b.scale)
        A = BigDecimal._pad_trailing(a.digits, S - a.scale)  # integer
        B = BigDecimal._pad_trailing(b.digits, S - b.scale)  # integer

        # Multiply A by 10^prec to generate fractional digits in quotient
        A_scaled = BigDecimal._pad_trailing(A, prec)

        q = BigDecimal._div_integer_trunc(A_scaled, B)  # integer division truncation
        # Remove leading zeros
        q = q.lstrip('0')
        if q == "":
            q = "0"

        sign = a.sign * b.sign
        return BigDecimal(sign, q, prec).normalize()

    @staticmethod
    def _pad_trailing(d: str, k: int) -> str:
        if k <= 0:
            return d
        return d + ("0" * k)

    @staticmethod
    def _div_integer_trunc(A: str, B: str) -> str:
        """
        Compute floor(A / B) where A, B are non-negative integer strings.
        Long division by repeated subtraction of multiples.
        Optimized with digit-wise long division.
        """
        if B == "0":
            raise ZeroDivisionError
        # If A < B, quotient is 0
        cmp = BigDecimal._cmp_digits(A, B)
        if cmp < 0:
            return "0"
        if B == "1":
            return A

        # Long division
        quotient = []
        remainder = "0"
        for ch in A:
            # remainder = remainder*10 + int(ch)
            remainder = BigDecimal._append_digit(remainder, ord(ch) - 48)
            # Find digit q such that B*q <= remainder < B*(q+1)
            q_digit = BigDecimal._estimate_div_digit(remainder, B)
            quotient.append(chr(48 + q_digit))
            # remainder -= B * q_digit
            if q_digit != 0:
                prod = BigDecimal._mul_digit(B, q_digit)
                remainder = BigDecimal._sub_digits(remainder, prod)
        # strip leading zeros
        q_str = "".join(quotient).lstrip('0')
        return q_str if q_str != "" else "0"

    @staticmethod
    def _append_digit(remainder: str, d: int) -> str:
        # remainder*10 + d
        if remainder == "0":
            return str(d)
        return remainder + chr(48 + d)

    @staticmethod
    def _estimate_div_digit(R: str, B: str) -> int:
        """
        Estimate the next quotient digit by trial (0..9).
        Could be improved with numeric approximations, but trial is robust.
        """
        # Fast path using length comparison
        for q in range(9, -1, -1):
            if q == 0:
                return 0
            prod = BigDecimal._mul_digit(B, q)
            cmp = BigDecimal._cmp_digits(prod, R)
            if cmp <= 0:
                return q
        return 0

    @staticmethod
    def _mul_digit(B: str, q: int) -> str:
        if q == 0 or B == "0":
            return "0"
        carry = 0
        out = []
        for i in range(len(B) - 1, -1, -1):
            bi = ord(B[i]) - 48
            s = bi * q + carry
            out.append(chr(48 + (s % 10)))
            carry = s // 10
        if carry:
            out.append(str(carry))
        res = "".join(reversed(out)).lstrip('0')
        return res if res != "" else "0"

    # ------------- Convenience operators -------------

    def __truediv__(self, other: "BigDecimal") -> "BigDecimal":
        # Default division precision
        return self.div(other, prec=50)

    # ------------- Helpers for construction -------------

    @staticmethod
    def from_int(n: int) -> "BigDecimal":
        if n == 0:
            return BigDecimal.zero()
        sign = 1 if n >= 0 else -1
        digits = str(abs(n))
        return BigDecimal(sign, digits, 0)

    @staticmethod
    def from_float(f: float) -> "BigDecimal":
        # Convert via string to avoid scientific notation issues
        s = format(f, ".17g")
        return BigDecimal.from_string(s)
