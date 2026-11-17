import importlib.util
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))

@unittest.skipUnless(importlib.util.find_spec('torch') is not None,'Teste opcional: requer ambiente de ML.')
class LoRATests(unittest.TestCase):
    def test_frozen_base_zero_initialization_update_and_merge(self):
        import torch
        from torch import nn
        from ml.lora import attach,adapter_state,merge
        torch.manual_seed(42)
        model=nn.Module();model.layer=nn.Module();model.layer.q_proj=nn.Linear(4,6)
        x=torch.randn(2,4)
        before=model.layer.q_proj(x).detach().clone();base=model.layer.q_proj.weight.detach().clone()
        attach(model,rank=2,alpha=4,dropout=0)
        self.assertTrue(torch.allclose(before,model.layer.q_proj(x)))
        self.assertFalse(model.layer.q_proj.base.weight.requires_grad)
        optimizer=torch.optim.SGD((p for p in model.parameters() if p.requires_grad),lr=.1)
        model.layer.q_proj(x).square().mean().backward();optimizer.step()
        self.assertTrue(torch.equal(base,model.layer.q_proj.base.weight))
        self.assertGreater(torch.count_nonzero(adapter_state(model)['layer.q_proj.lora_B']).item(),0)
        adapted=model.layer.q_proj(x).detach().clone()
        merge(model)
        self.assertTrue(torch.allclose(adapted,model.layer.q_proj(x),atol=1e-6))

if __name__=='__main__':unittest.main()
