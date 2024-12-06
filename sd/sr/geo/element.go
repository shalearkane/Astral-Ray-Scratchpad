package geo

import "math"

type Element struct {
	Al   float64 `json:"al"`
	Fe   float64 `json:"fe"`
	Mg   float64 `json:"mg"`
	Si   float64 `json:"si"`
	Na   float64 `json:"na"`
	Ca   float64 `json:"ca"`
	Ti   float64 `json:"ti"`
	O    float64 `json:"o"`
	Norm float64 `json:"norm"`
}

type ElementMatrices struct {
	Mg   [][]float64 `json:"mg"`
	Fe   [][]float64 `json:"fe"`
	Al   [][]float64 `json:"al"`
	Si   [][]float64 `json:"si"`
	Na   [][]float64 `json:"na"`
	Ca   [][]float64 `json:"ca"`
	Ti   [][]float64 `json:"ti"`
	O    [][]float64 `json:"o"`
	Norm [][]float64 `json:"norm"`
}

func NewElementWithDefault(n float64) Element {
	return Element{n, n, n, n, n, n, n, n, n}
}

func (e Element) Multiply(n float64) Element {
	return Element{
		Al:   e.Al * n,
		Fe:   e.Fe * n,
		Mg:   e.Mg * n,
		Si:   e.Si * n,
		Na:   e.Na * n,
		Ca:   e.Ca * n,
		Ti:   e.Ti * n,
		O:    e.O * n,
		Norm: e.Norm * n,
	}
}

func (e Element) Max(o Element) Element {
	return Element{
		Al:   math.Max(e.Al, o.Al),
		Fe:   math.Max(e.Fe, o.Fe),
		Mg:   math.Max(e.Mg, o.Mg),
		Si:   math.Max(e.Si, o.Si),
		Na:   math.Max(e.Na, o.Na),
		Ca:   math.Max(e.Ca, o.Ca),
		Ti:   math.Max(e.Ti, o.Ti),
		O:    math.Max(e.O, o.O),
		Norm: math.Max(e.Norm, o.Norm),
	}
}

func (e Element) Min(o Element) Element {
	return Element{
		Al:   math.Min(e.Al, o.Al),
		Fe:   math.Min(e.Fe, o.Fe),
		Mg:   math.Min(e.Mg, o.Mg),
		Si:   math.Min(e.Si, o.Si),
		Na:   math.Min(e.Na, o.Na),
		Ca:   math.Min(e.Ca, o.Ca),
		Ti:   math.Min(e.Ti, o.Ti),
		O:    math.Min(e.O, o.O),
		Norm: math.Min(e.Norm, o.Norm),
	}
}

func (e Element) Divide(n float64) Element {
	return Element{
		Al:   e.Al / n,
		Fe:   e.Fe / n,
		Mg:   e.Mg / n,
		Si:   e.Si / n,
		Na:   e.Na / n,
		Ca:   e.Ca / n,
		Ti:   e.Ti / n,
		O:    e.O / n,
		Norm: e.Norm / n,
	}
}

func (e Element) Add(other Element) Element {
	return Element{
		Al:   e.Al + other.Al,
		Fe:   e.Fe + other.Fe,
		Mg:   e.Mg + other.Mg,
		Si:   e.Si + other.Si,
		Na:   e.Na + other.Na,
		Ca:   e.Ca + other.Ca,
		Ti:   e.Ti + other.Ti,
		O:    e.O + other.O,
		Norm: e.Norm + other.Norm,
	}
}

func (e Element) DivideElement(other Element) Element {
	return Element{
		Al:   e.Al / other.Al,
		Fe:   e.Fe / other.Fe,
		Mg:   e.Mg / other.Mg,
		Si:   e.Si / other.Si,
		Na:   e.Na / other.Na,
		Ca:   e.Ca / other.Ca,
		Ti:   e.Ti / other.Ti,
		O:    e.O / other.O,
		Norm: e.Norm / e.Norm,
	}
}

func (e Element) MultiplyElement(other Element) Element {
	return Element{
		Al:   e.Al * other.Al,
		Fe:   e.Fe * other.Fe,
		Mg:   e.Mg * other.Mg,
		Si:   e.Si * other.Si,
		Na:   e.Na * other.Na,
		Ca:   e.Ca * other.Ca,
		Ti:   e.Ti * other.Ti,
		O:    e.O * other.O,
		Norm: e.Norm * e.Norm,
	}
}
