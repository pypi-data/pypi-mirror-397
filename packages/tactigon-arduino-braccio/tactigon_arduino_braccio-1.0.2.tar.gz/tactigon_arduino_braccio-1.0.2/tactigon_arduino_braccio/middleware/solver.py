from math import degrees

import sympy


class Solver:
    l0 = 71.5
    l1 = 125
    l2 = 125
    l3 = 60 + 132

    def move_to_position_cart(self, x, y, z):
        r_compensation = 1.02  # add 2 percent
        z = z + 15  # compensation for backlash
        r_hor = sympy.sqrt(x ** 2 + y ** 2)
        r = sympy.sqrt(r_hor ** 2 + (z - 71.5) ** 2) * r_compensation  # type: ignore

        if y < 0:
            raise Exception()

        if y == 0:
            if x <= 0:
                theta_base = 180
            else:
                theta_base = 0
        else:
            theta_base = 90 - degrees(sympy.atan(x / y))  # add 2 degrees for backlash compensation
        # print(theta_base)
        # theta_base=backlash_compensation_base(theta_base)  #check if compensation is needed

        # calulcate angles for level operation

        alpha1 = sympy.acos(((r - self.l2) / (self.l1 + self.l3)))
        theta_shoulder = degrees(alpha1)
        # compensate for the difference in arm length
        alpha3 = sympy.sin((sympy.sin(alpha1) * self.l3 - sympy.sin(alpha1) * self.l1) / self.l2)  # type: ignore
        theta_elbow = (90 - degrees(alpha1)) + degrees(alpha3)
        theta_wrist = (90 - degrees(alpha1)) - degrees(alpha3)

        if theta_wrist <= 0:  # when arm length compensation results in negative values
            alpha1 = sympy.acos(((r - self.l2) / (self.l1 + self.l3)))
            theta_shoulder = degrees(alpha1 + sympy.sin((self.l3 - self.l1) / r))  # type: ignore
            theta_elbow = (90 - degrees(alpha1))
            theta_wrist = (90 - degrees(alpha1))

        # adjust shoulder angle to increase heigth
        if z != self.l0:
            theta_shoulder = theta_shoulder + degrees(sympy.atan(((z - self.l0) / r)))
            # print(degrees(sympy.atan(((z-self.l0)/r))))

        # add compensation for bad line-up of servo with mount
        theta_elbow = theta_elbow + 5
        theta_wrist = theta_wrist + 5

        theta_array = [round(theta_base), round(theta_shoulder), round(theta_elbow), round(theta_wrist)]

        return theta_array


if __name__ == "__main__":
    s = Solver()
    cart = s.move_to_position_cart(100, 100, 0)

    print(cart)
