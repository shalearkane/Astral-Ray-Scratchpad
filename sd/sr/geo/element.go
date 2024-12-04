package geo

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
