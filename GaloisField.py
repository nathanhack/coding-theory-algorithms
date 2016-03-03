import numpy as np

"""
If not specified differently, all functions use
the integer representation to denote elements in
the GF.

Example for GF(16) generated by 1 + X + X^4

Int. rep.   Exp. rep.     vector rep.  =  poly. rep.
--------------------------------------------------------
0           -INF          [0 0 0 0]       0
1           α^0           [1 0 0 0]       1
2           α^1           [0 1 0 0]       α
3           α^2           [0 0 1 0]       α^2
4           α^3           [0 0 0 1]       α^3
5           α^4           [1 1 0 0]       1 + α
6           α^5           [0 1 1 0]       α + α^2
7           α^6           [0 0 1 1]       α^2 + α^3
8           α^7           [1 1 0 1]       1 + α + α^3
9           α^8           [1 0 1 0]       1 + α^2
10          α^9           [0 1 0 1]       α + α^3
11          α^10          [1 1 1 0]       1 + α + α^2
12          α^11          [0 1 1 1]       α + α^2 + α^3
13          α^12          [1 1 1 1]       1 + α + α^2 + α^3
14          α^13          [1 0 1 1]       1 + α^2 + α^3
15          α^14          [1 0 0 1]       1 + α^3
"""

def degree(p):
    """Returns degree of polynomial (highest exponent).
    (slide 3)
    """
    poly = np.poly1d(np.flipud(p))
    return poly.order

def X(i):
    """Create single coefficient polynomial with degree i: X^i
    """
    X = np.zeros(i + 1)
    X[i] = 1
    return X.astype(int)

def constructGF(p, verbose = True):
    """Construct GF(2^m) based on primitive polynomial p.
    The degree of pi(X) is used to determine m.
    (slide 12)
    Args:
        p: primitive polynomial p to construct the GF with.
        verbose: print information on how the GF is constructed.
    Returns:
        Elements of the GF in polynomial representation.
    """
    elements = []
    m = degree(p)

    if m == 1: # special simple case: GF(2)
        elements = [np.array([0]), np.array([1])]
        return elements

    a_high = p[:m] # see slide 12 Solution

    if verbose:
        print()
        print('Construct a GF(2^' + str(m) + ') based on primitive')
        print('polynomial pi(X) =', GF2.polyToString(p, 'X'))
        print()
        print(u'Assuming pi(X) has root \u03B1, there is')
        print(u'pi(\u03B1) =', GF2.polyToString(p, '\u03B1'), '= 0,')
        print(u'then \u03B1^' + str(m) + ' = ' + GF2.polyToString(a_high, u'\u03B1'))
        print()
        print('Exp. rep.\t vector rep.\t poly. rep.')
        print('-------------------------------------------')

    for i in range(0, 2**m):
        # create exponential representation
        if i == 0:
            exp = np.array([0])
        else:
            exp = X(i-1)

        # create polynomial representation (CAN'T EXPLAIN...IT'S MAGIC)
        poly = exp
        if degree(poly) >= m:
            quotient, remainder = divmod(degree(poly), m)

            poly = X(remainder)
            for j in range(0, quotient):
                poly = GF2.multPoly(poly, a_high)

            while degree(poly) >= m:
                poly = GF2.addPoly(poly, elements[degree(poly) + 1])
                poly = poly[:-1]

        # format polynomial (size m)
        poly = poly[:degree(poly) + 1]
        poly = np.pad(poly, (0, m - poly.size), 'constant', constant_values = 0)

        # append to elements list for return
        elements.append(poly.astype(int))

        # print row
        if verbose:
            expStr = GF2.polyToString(exp, u'\u03B1')
            polyStr = GF2.polyToString(poly, u'\u03B1')
            print(expStr, '\t\t', poly, '\t', polyStr)

    if verbose:
        print()
    return elements

class GaloisField:
    """Galois Field GF(2^m)

    Based on the the Galois Field lecture (2016-18-02).

    Attributes:
        _p: Primitive polynomial pi(X) the GF is based on.
        _cachedPolyElements: All elements of the GF in polynomial representation
    """
    _p = np.zeros(1)
    _cachedPolyElements = []

    def __init__(self, p = np.array([1, 1])):
        """Create Galois Field GF(2^m)
        The degree of pi(X) is used to determine m.

        Args:
            p: Primitive polynomial pi(X) the GF is based on.
               (default: 1+X -> GF(2))
        """
        self._p = p
        self._cachedPolyElements = constructGF(self.p(), False)

    def p(self):
        """Primitive polynomial pi(X) the GF is based on.
        """
        return self._p.astype(int)

    def m(self):
        """GF(2^m) -> returns m
        """
        return degree(self.p())

    def q(self):
        return len(self._cachedPolyElements)

    def printInfo(self):
        """Prints how the GF is constructed from the primitive
        polynomial pi(X).
        """
        constructGF(self.p(), True)

        """ slide 17: """
        m = self.m()
        tmp = self.addPoly(X(0), X(2**m-1)) # x^(2^m - 1) + 1
        print('-> The non-zero elements of GF(2^' + str(self.m()) + \
              ') are all roots of ' + self.polyToString(tmp) + '.')

        tmp = self.addPoly(X(0), X(2**m))
        print('-> The elements of GF(2^' + str(self.m()) + \
              ') are all roots of ' + self.polyToString(tmp) + '.')
        print()

    def elementsAsPoly(self):
        """All elements of the GF in polynomial representation.
        """
        return self._cachedPolyElements

    def element(self, a):
        """Return element that is the same as element a but with an
        exponent within 0 and q-1.
        """
        if a == 0: # zero element doesn't have an exponent
            return int(a)
        exp_a = a - 1 # convert from integer representation to exponent
        exp_a = exp_a % (self.q() - 1) # get exponent within 0 and q-1
        a = exp_a + 1 # convert back to integer representation
        return int(a)

    def elementToExp(self, a):
        """Returns the exponent of an element. For the zero element an exponent
        of -infinity is returned by definition.
        """
        a = self.element(a) # element with exponent within 0 and q-1
        if a == 0: # zero element is special case
            return -INF
        exp_a = a - 1 # convert from integer representation to exponent
        return int(exp_a)

    def elementFromExp(self, exp_a):
        """Returns element in integer representation from given exponent
        representation. For the zero element an exponent of +-infinity is
        expected by definition.
        """
        if exp_a == INF or exp_a == -INF: # zero element is special case
            return 0
        a = exp_a + 1 # convert to integer representation
        a = self.element(a) # element with exponent within 0 and q-1
        return int(a)

    def elementToPoly(self, a, size_m = False):
        """Return element in polynomial representation.
        """
        a = self.element(a) # element with exponent within 0 and q-1
        poly_a = self.elementsAsPoly()[a]
        if size_m:
            poly_a = np.pad(poly_a, (0, self.m() - poly_a.size), \
                        'constant', constant_values = 0)
        return poly_a.astype(int)

    def elementFromPoly(self, poly_a):
        """Return element from given element in polynomial representation.
        """
        assert degree(poly_a) <= degree(self.p())
        poly_a = poly_a[:degree(poly_a) + 1] # remove dangling zeros
        for i, poly_i in enumerate(self.elementsAsPoly()):
            poly_i = poly_i[:degree(poly_i) + 1] # remove dangling zeros
            if np.array_equal(poly_i, poly_a):
                return int(i)
        assert False, "This should never be reached?!"

    def addElements(self, a, b):
        """Add two elements of the GF.
        """
        poly_a = self.elementToPoly(a, True)
        poly_b = self.elementToPoly(b, True)
        poly_sum = (poly_a + poly_b) % 2
        return int(self.elementFromPoly(poly_sum))

    def multElements(self, a, b):
        """Multiply two elements of the GF.
        """
        exp_a = self.elementToExp(a)
        exp_b = self.elementToExp(b)
        exp_product = exp_a + exp_b # multiplication = adding the exponents
        product = self.elementFromExp(exp_product)
        return int(product)

    def divElements(self, a, b):
        """Divide two elements of the GF (a / b).
        (Get remainder with modElement function)
        """
        exp_a = self.elementToExp(a)
        exp_b = self.elementToExp(b)
        exp_q = exp_a - exp_b # division = subtracting the exponents
        q = self.elementFromExp(exp_q)
        return int(q)

    def powElement(self, a, exponent):
        """Power the exlement a times exponent (a^exponent)
        """
        exp_a = self.elementToExp(a)
        exp_power = exp_a * exponent
        power = self.elementFromExp(exp_power)
        return int(power)

    def addPoly(self, a, b):
        """Add two polynomials in the GF.
        """
        summ_degree = max(degree(a), degree(b))
        summ = np.zeros(summ_degree + 1)
        for i in range(0, summ.size):
            if i > a.size - 1:
                summ[i] = b[i]
            elif i > b.size - 1:
                summ[i] = a[i]
            else:
                summ[i] = self.addElements(a[i], b[i])
        return summ.astype(int)

    def multPoly(self, a, b):
        """Multiply two polynomials in the GF.
        """
        product_max_degree = degree(a) + degree(b)
        product = np.zeros(product_max_degree + 1)
        for i in range(0, degree(a) + 1):
            for j in range(0, degree(b) + 1):
                product_tmp = self.multElements(a[i], b[j])
                product[i + j] = self.addElements(product[i + j], product_tmp)
        product = product[:degree(product) + 1] # remove dangling zeros
        return product.astype(int)

    def divmodPoly(self, a, b, verbose = False):
        """Divide two polynomials in the GF (a/b) and return quotient and
        remainder in python array. See divPoly() and modPoly() for only quotient
        and remainder respectively.
        """
        assert np.count_nonzero(b) > 0, "Division by zero!"
        if verbose:
            print()
            print('Division:')
            print(self.polyToString(a) + ' / '  + self.polyToString(a) + ' :')
            print()
        q = np.zeros(0)
        while degree(a) >= degree(b):
            exp_a = degree(a)
            exp_b = degree(b)
            coeff_element_a = a[exp_a]
            coeff_element_b = b[exp_b]
            multiplier = np.zeros(degree(a) - degree(b) + 1)
            multiplier[exp_a - exp_b] = self.divElements(coeff_element_a, coeff_element_b)
            subtrahend = self.multPoly(b, multiplier)
            if verbose:
                print(self.polyToString(a, 'X', True))
                print(self.polyToString(subtrahend, 'X', True))
                print("--------------------------------")
            a = self.addPoly(a, subtrahend) # addition = subtraction
            q = self.addPoly(q, multiplier)
        remainder = a
        if verbose:
            print(self.polyToString(a, 'X', True))
            print()
            print('q = ' + self.polyToString(q))
            print('remainder = ' + self.polyToString(remainder))
            print()
        return [q, remainder]

    def divPoly(self, a, b):
        """Divide two polynomials in the GF (a/b) and return quotient.
        """
        return self.divmodPoly(a, b)[0]

    def modPoly(self, a, b):
        """Divide two polynomials in the GF (a/b) and return remainder.
        """
        return self.divmodPoly(a, b)[1]

    def isFactor(self, p, factorPoly):
        """Check if polynomial factorPoly is a factor of polynomial p.
        (remainder == [0])
        """
        remainder = self.modPoly(p, factorPoly)
        return np.count_nonzero(remainder) == 0

    def substituteElementIntoPoly(self, p, a):
        """Subsitute element a into polynomial p and return resulting
        element.
        """
        result = 0
        for i in range(0, p.size):
            tmp = self.powElement(a, i)
            tmp = self.multElements(tmp, p[i])
            result = self.addElements(result, tmp)
        return int(result)

    def elementToString(self, a):
        """Returns element as string (e.g. 'a^5')
        """
        if a == 0:
            return '0'
        elif a == 1:
            return '1'
        else:
            return u'\u03B1^' + str(self.elementToExp(a))

    def polyToString(self, p, variable = 'X', reverse = False):
        """Returns polynomial in string representation.
        E.g. [0,1,0,3] -> "X + a^2*X^3"
            or
             [0,1,0,3] -> "a^2*X^3 + X" if reverse == True
        Args:
            p: polynomial
            variable: polynomial variable character
        Returns:
            Polynomial p in string representation.
        """
        if type(p) is int:
            p = np.array([p])
        s = ''

        if reverse:
            index_list = range(p.size - 1, -1, -1)
        else:
            index_list = range(0, p.size)

        for i in index_list:
            coeff_element = p[i]
            if coeff_element != 0:
                if s != '':
                    s += ' + '
                if coeff_element > 1:
                    s += self.elementToString(coeff_element)
                    if i > 0:
                        s += '*'
                if i > 0:
                    s += variable
                    if i > 1:
                        s += '^' + str(i)
                elif coeff_element == 1:
                    s+= '1'
        if s == '':
            s = '0'
        return s

    def roots(self, p):
        """Substitutes all non-zero elements of the GF into polynomial p to
        find roots and returns them in a standard python array.
        (Chien search)
        Args:
            p: polynomial to find roots for in the GF.
        Returns:
            Roots of p in the GF as standard python array.
        """
        roots = []
        for element in range(1, self.q()):
            result = self.substituteElementIntoPoly(p, element)
            if result == 0:
                roots.append(element)
        return roots

    def conjugateRoots(self, root, verbose = False):
        """
        Conjugate a known root (alpha^i = beta) to all other
        roots (beta^(2^l)) of this conjugate root group and
        return them.
        (slide 16)
        Args:
            root: known root
            verbose: print info on how this is calculated
        Returns:
            Sorted conjugate roots group in the GF as standard
            python array.
        """
        if verbose:
            print()
        roots = []
        l = 0
        while True:
            l += 1
            new_root = self.powElement(root, 2**l)
            if verbose:
                print('l = ' + str(l) + ':\t(' + self.elementToString(root) + \
                      ')^' + str(2**l) + ' = ' + self.elementToString(new_root))
            roots.append(new_root)
            if new_root == root:
                break
        if verbose:
            print()
        return sorted(roots)

    def removeConjugateRoots(self, roots):
        """Remove all conjugate roots from given roots list and leave only
        lowest root.
        """
        result = roots
        for root in roots:
            conjugateRoots = self.conjugateRoots(root)
            for conjugateRoot in conjugateRoots[1:]: # don't remove first root
                if conjugateRoot in result:
                    result.remove(conjugateRoot)
        return result

    def conjugateRootGroups(self):
        """Calculate all conjugate groups and return them in a
        python array.
        """
        groups = [[0]]
        m = self.m()
        for i in range(0, 2**m-1):
            group = self.conjugateRoots(i)
            if group not in groups:
                groups.append(group)
        return groups

    def minimalPolynomial(self, roots):
        """Generate minimal polynomial from conjugate root group.
        Args:
            conjugateRoots: Exponent of roots in a standard python array.
        """
        result = np.ones(1)
        for root in roots:
            root_poly = np.array([root, 1]) # (root + X)
            result = self.multPoly(result, root_poly)
        return result.astype(int)

    def printMinimalPolynomials(self):
        """Print all conjugate root groups and their corresponding
        minimal polynomial.
        """
        print()
        print('Conjugate roots  ->  Minimal polynomials')
        print('----------------------------------------')
        for roots in self.conjugateRootGroups():
            rootStr = ''
            for root in roots:
                rootStr += self.elementToString(root) + ', '
            rootStr = rootStr[:-2] # remove last comma
            minPoly = self.minimalPolynomial(roots)
            print(rootStr, '\t', GF2.polyToString(minPoly))
        print()

    def irreducible(self, p, verbose = False):
        """
        Test all factor polynomials over GF of degree higher than
        zero and lower than m to see if p has no factor polynomial and
        thus is irreducible ofer GF(2).
        (slide 6)
        Args:
            p: polynomial to check if irreducible over GF(2)
        Returns:
            True if polynomial is irreducible.
        """
        m = self.m()
        irreducible = True
        if verbose:
            print()
            s = ''
        for factorPoly in self.elementsAsPoly():
            if not (0 < degree(factorPoly) < m):
                continue
            if self.isFactor(p, factorPoly):
                if verbose:
                    irreducible = False
                    s += '\n' + self.polyToString(factorPoly)
                else:
                    return False # skip all other tests
        if verbose:
            if irreducible:
                print('The polynomial', self.polyToString(p), \
                      'is irreducible over GF(2), since \nit has no', \
                      'factor polynomials over GF(2) of degree higher than\n'+ \
                      'zero and lower than ' + str(m) + '.')
            else:
                print('The polynomial', self.polyToString(p), \
                      'is NOT irreducible over GF(2).\n' + \
                      'It has the following factor polynomials:' + s)
        if verbose:
            print()
        return irreducible

    def primitive(self, p, verbose = False):
        """
        Test of polynomial is primitive (and hence also irreducible).
        (slide 7)
        Args:
            p: polynomial to check if primitive
        Returns:
            True if polynomial is primitive.
        """
        if not self.irreducible(p, verbose):
            if verbose:
                print('Hence, the polynomial is also not primitive.')
            return False
        else: # irreducible
            m = self.m()
            for n in range(1, 2**m-1):
                p2 = self.addPoly(X(0), X(n))
                if self.isFactor(p2, p):
                    if verbose:
                        print('The polynomial', self.polyToString(p), \
                              'is a factor polynomial of 1+X^' + str(n) + '\n' + \
                              'and hence not primitive.')
                    return False
        if verbose:
            print('The polynomial', self.polyToString(p), 'is also primitive,',\
                  'since it is not a \nfactor of 1+X^n, 1 <= n < ' + \
                  str(2**m-1) + '.\n')
        return True

INF = float('inf') # infinity variable
GF2 = GaloisField() # global GF(2) field
