import json
from pathlib import Path
from typing import Dict

import pdg
from particle import Particle as Particle_external

here = Path(__file__).parent

class Particle:
    _file_cache = None
    _api_cache = {}  # 缓存结构：{mcid: 粒子API属性字典}

    def __init__(self, name: str = None, mcid: int = None, **kwargs):
        self.name = name
        self.mcid = int(mcid) if mcid else None

        if mcid is None and name is None:
            raise ValueError("Either 'name' or 'mcid' must be provided")
        
        # 1. 加载本地数据库数据
        local_item = self._get_local_item()
        if not local_item:
            query_info = f"name='{name}', mcid={mcid}"
            raise ValueError(f"Particle with {query_info} not found in database")
        self._initialize_from_local_db(local_item)

        # 2. 处理外部API缓存 + 调用
        try:
            if self.mcid in self._api_cache:
                # 缓存命中：直接从缓存加载API属性
                api_data = self._api_cache[self.mcid]
                self._bind_api_data_to_instance(api_data)
            else:
                # 缓存未命中：调用API并更新缓存
                api_data = self._initialize_from_external_api()
                self._api_cache[self.mcid] = api_data
        except Exception as e:
            print(f"Error in Particle ({self.name}, mcid={self.mcid}) initialization from external API: {e}")
            self._api_cache[self.mcid] = {}

        # 3. 设置额外属性
        self.mother = kwargs.get("mother")
        self.children = kwargs.get("children", [])
        self.id = kwargs.get("id")

    def _get_local_item(self) -> Dict:
        """抽取公共方法：根据name或mcid查询本地数据库"""
        if self.mcid:
            return self.match_particle_mcid(self.mcid)
        else:
            return self.match_particle_name(self.name)

    def _initialize_from_local_db(self, item):
        """从本地数据库初始化基本属性"""
        self.name = item.get("name", "unknown")
        self.mcid = item.get("mcid", 0)
        self.programmatic_name = item.get("programmatic_name", str(self.mcid))
        self.latex_name = item.get("latex_name", str(self.mcid))
        self.evtgen_name = item.get("evtgen_name", str(self.mcid))
        self.html_name = item.get("html_name", str(self.mcid))
        self.unicode_name = item.get("unicode_name", str(self.mcid))

        # 设置默认值（原有逻辑保留）
        self.branching_fractions = item.get('branching_fractions', None)
        self.charge = item.get('charge', None)
        self.exclusive_branching_fractions = item.get('exclusive_branching_fractions', None)
        self.has_lifetime_entry = item.get('has_lifetime_entry', None)
        self.has_mass_entry = item.get('has_mass_entry', None)
        self.has_width_entry = item.get('has_width_entry', None)
        self.inclusive_branching_fractions = item.get('inclusive_branching_fractions', None)
        self.is_baryon = item.get('is_baryon', None)
        self.is_boson = item.get('is_boson', None)
        self.is_lepton = item.get('is_lepton', None)
        self.is_meson = item.get('is_meson', None)
        self.is_quark = item.get('is_quark', None)
        self.lifetime = item.get('lifetime', None)
        self.lifetime_err = item.get('lifetime_err', None)
        self.mass = item.get('mass', None)
        self.mass_err = item.get('mass_err', None)
        self.quantum_C = item.get('quantum_C', None)
        self.quantum_G = item.get('quantum_G', None)
        self.quantum_I = item.get('quantum_I', None)
        self.quantum_J = item.get('quantum_J', None)
        self.quantum_P = item.get('quantum_P', None)
        self.width = item.get('width', None)
        self.width_err = item.get('width_err', None)

    def _bind_api_data_to_instance(self, api_data: Dict):
        """将缓存的API数据绑定到实例属性"""
        for key, value in api_data.items():
            setattr(self, key, value)
        self.api_properties = api_data

    def _initialize_from_external_api(self) -> Dict:
        """从外部API获取更多属性"""
        api = pdg.connect()
        particle = api.get_particle_by_mcid(self.mcid)
        api_data = {}  # 整理API数据到字典（用于缓存）

        # 逐个属性判断并获取 + 同步更新api_data和实例属性
        if self.branching_fractions is None:
            self.branching_fractions = particle.branching_fractions()
            self.branching_fractions = [
                {"description": bf.description, "is_limit": bf.is_limit, "value": bf.value}
                for bf in self.branching_fractions
            ]
            api_data["branching_fractions"] = self.branching_fractions

        if self.charge is None:
            self.charge = particle.charge
            api_data["charge"] = self.charge

        if self.exclusive_branching_fractions is None:
            self.exclusive_branching_fractions = particle.exclusive_branching_fractions()
            self.exclusive_branching_fractions = [
                {"description": bf.description, "is_limit": bf.is_limit, "value": bf.value}
                for bf in self.exclusive_branching_fractions
            ]
            api_data["exclusive_branching_fractions"] = self.exclusive_branching_fractions

        if self.has_lifetime_entry is None:
            self.has_lifetime_entry = particle.has_lifetime_entry
            api_data["has_lifetime_entry"] = self.has_lifetime_entry

        if self.has_mass_entry is None:
            self.has_mass_entry = particle.has_mass_entry
            api_data["has_mass_entry"] = self.has_mass_entry

        if self.has_width_entry is None:
            self.has_width_entry = particle.has_width_entry
            api_data["has_width_entry"] = self.has_width_entry

        if self.inclusive_branching_fractions is None:
            self.inclusive_branching_fractions = particle.inclusive_branching_fractions()
            self.inclusive_branching_fractions = [
                {"description": bf.description, "is_limit": bf.is_limit, "value": bf.value}
                for bf in self.inclusive_branching_fractions
            ]
            api_data["inclusive_branching_fractions"] = self.inclusive_branching_fractions

        if self.is_baryon is None:
            self.is_baryon = particle.is_baryon
            api_data["is_baryon"] = self.is_baryon

        if self.is_boson is None:
            self.is_boson = particle.is_boson
            api_data["is_boson"] = self.is_boson

        if self.is_lepton is None:
            self.is_lepton = particle.is_lepton
            api_data["is_lepton"] = self.is_lepton

        if self.is_meson is None:
            self.is_meson = particle.is_meson
            api_data["is_meson"] = self.is_meson

        if self.is_quark is None:
            self.is_quark = particle.is_quark
            api_data["is_quark"] = self.is_quark

        if self.lifetime is None:
            try:
                self.lifetime = particle.lifetime
            except:
                self.lifetime = -1
            api_data["lifetime"] = self.lifetime

        if self.lifetime_err is None:
            try:
                self.lifetime_err = particle.lifetime_error
            except:
                self.lifetime_err = -1
            api_data["lifetime_err"] = self.lifetime_err

        if self.mass is None:
            self.mass = particle.mass
            api_data["mass"] = self.mass

        if self.mass_err is None:
            self.mass_err = particle.mass_error
            api_data["mass_err"] = self.mass_err

        if self.quantum_C is None:
            self.quantum_C = particle.quantum_C
            api_data["quantum_C"] = self.quantum_C

        if self.quantum_G is None:
            self.quantum_G = particle.quantum_G
            api_data["quantum_G"] = self.quantum_G

        if self.quantum_I is None:
            self.quantum_I = particle.quantum_I
            api_data["quantum_I"] = self.quantum_I

        if self.quantum_J is None:
            self.quantum_J = particle.quantum_J
            api_data["quantum_J"] = self.quantum_J

        if self.quantum_P is None:
            self.quantum_P = particle.quantum_P
            api_data["quantum_P"] = self.quantum_P

        if self.width is None:
            self.width = particle.width
            api_data["width"] = self.width

        if self.width_err is None:
            self.width_err = particle.width_error
            api_data["width_err"] = self.width_err

        # 使用 Particle 包获取额外信息
        particle_ex = Particle_external.findall(lambda p: p.pdgid == self.mcid)
        if particle_ex:
            if self.programmatic_name is None:
                self.programmatic_name = particle_ex[0].programmatic_name
                api_data["programmatic_name"] = self.programmatic_name
            if self.latex_name is None:
                self.latex_name = particle_ex[0].latex_name
                api_data["latex_name"] = self.latex_name
            if self.evtgen_name is None:
                self.evtgen_name = particle_ex[0].evtgen_name
                api_data["evtgen_name"] = self.evtgen_name
            if self.html_name is None:
                self.html_name = particle_ex[0].html_name
                api_data["html_name"] = self.html_name
            if self.unicode_name is None:
                self.unicode_name = particle_ex[0].unicode_name
                api_data["unicode_name"] = self.unicode_name

        return api_data  # 返回整理后的字典，用于缓存

    @staticmethod
    def match_particle_name(name: str) -> Dict:
        """从本地数据库匹配粒子名称"""
        if Particle._file_cache is None:
            cache_path = here / "particle_variants.json"
            with open(cache_path, "r") as f:
                Particle._file_cache = json.load(f)
        
        for item in Particle._file_cache:
            fields = {
                item["name"],
                item["programmatic_name"],
                item["latex_name"],
                item["evtgen_name"],
                item["html_name"],
                item["unicode_name"],
            }
            fields.update(item["aliases"])
            if name and name in fields:
                return item
        return {}
    
    @staticmethod
    def match_particle_mcid(mcid: int) -> Dict:
        """从本地数据库匹配粒子MCID（修复：冗余逻辑简化）"""
        if Particle._file_cache is None:
            cache_path = here / "particle_variants.json"
            with open(cache_path, "r") as f:
                Particle._file_cache = json.load(f)
        
        for item in Particle._file_cache:
            if mcid and item["mcid"] == mcid:
                return item
        return {}
    


if __name__ == "__main__":
    # 基本粒子
    eplus = Particle("e+")
    xxx = Particle(mcid=1114)
    muplus = Particle("mu+")
    muminus = Particle("mu-")
    piplus = Particle("pi+")
    piminus = Particle("pi-")
    pizero = Particle("pi0")
    kplus = Particle("K+")
    kminus = Particle("K-")
    k0 = Particle("K0")
    ks0 = Particle("K(S)0")
    kl0 = Particle("K(L)0")
    proton = Particle("p")
    antiproton = Particle("pbar")

    # 介子
    rho0 = Particle("rho0")
    rhoplus = Particle("rho+")
    kstar = Particle("K*0")

    # 重子
    lambda1 = Particle("Lambda")
    antilambda = Particle("Lambdabar")

    # 轻子
    eta = Particle("eta")
    gamma = Particle("gamma")

    # 粲夸克相关粒子
    jpsi = Particle("J/psi")
    psi2S = Particle("psi(2S)")
    psi3770 = Particle("psi(3770)")
    psi4260 = Particle("psi(4260)")

    # 其他
    phi = Particle("phi")
    f0980 = Particle("f_0(980)0")
    print()


    print("-"*80)
    print(f"rho0 name in pdg: {rhoplus.name}")
    # for bf in jpsi.branching_fractions:
    #     print('%-60s    %4s    %s' % (bf.get('description', ''), bf.get('is_limit', ''), bf.get('value', '')))

    print("-"*80)
    for bf in rhoplus.exclusive_branching_fractions:
        print('%-60s    %4s    %s' % (bf.get('description', ''), bf.get('is_limit', ''), bf.get('value', '')))
    
    # print("-"*80)
    # for bf in jpsi.inclusive_branching_fractions:
    #     print('%-60s    %4s    %s' % (bf.get('description', ''), bf.get('is_limit', ''), bf.get('value', '')))
    
    # print("-"*80)
    # print(jpsi.inclusive_branching_fractions)
