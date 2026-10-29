import numpy as np
import pytest
from wafer_data import CLASS_NAMES, die_counts, label_to_class, load_eligible

def test_nine_classes():
    assert len(CLASS_NAMES)==9
    assert label_to_class(np.zeros(8,dtype=int))==0
    for i in range(8):
        a=np.zeros(8,dtype=int);a[i]=1
        assert label_to_class(a)==i+1
    with pytest.raises(ValueError):
        label_to_class([1,1,0,0,0,0,0,0])

def test_die_counts():
    a=np.zeros((52,52),dtype=int)
    assert die_counts(a)["fail_ratio"]==0.
    a[5,6]=1;a[5,7]=2
    assert die_counts(a)["fail_ratio"]==.5
    a[5,8]=3
    with pytest.raises(ValueError): die_counts(a)

def test_quarantined_code(tmp_path):
    x=np.zeros((4,52,52),dtype=int);y=np.zeros((4,8),dtype=int)
    y[1,1]=1;y[2,[0,1]]=1;x[3,5,6]=3
    p=tmp_path/"test.npz";np.savez(p,arr_0=x,arr_1=y)
    maps,labels,indices,audit=load_eligible(p)
    assert len(maps)==2
    assert labels.tolist()==[0,2]
    assert indices.tolist()==[0,1]
    assert audit["excluded_mixed_defect"]==1
    assert audit["excluded_undocumented_die_value"]==1
