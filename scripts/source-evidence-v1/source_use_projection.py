"""Lossless typed projection of existing programme evidence; no tag allocator.

Artifact fingerprints below identify bytes, not bibliographic works or global
mathematical results. Existing IDs and native records remain authoritative.
"""
import copy, hashlib, json, re

def encoded(value): return (json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
def digest(value): return hashlib.sha256(encoded(value)).hexdigest()
def need(ok,message):
    if not ok: raise ValueError(message)
def pin(value):
    need(isinstance(value,str) and re.fullmatch('[0-9a-fA-F]{64}',value),'Invalid SHA-256')
    return value.lower()
def relpath(value):
    need(isinstance(value,str) and value and not value.startswith(('/','\\')) and ':' not in value and '\\' not in value and '..' not in value.split('/'),'Unsafe portable path')
    return value
def ref(kind,key): return {'kind':kind,'id':key}
def route_key(route):
    # Reuse an existing native identity or exact manifest locator. Do not
    # allocate a new mathematical tag for a route that never had one.
    key=route.get('id') or route.get('native_provider') or route.get('reader_manifest')
    need(isinstance(key,str) and key,'Route has no supplied stable identity')
    return key

def source_uses(bundle):
    """Index existing source-use declarations without allocating source keys.

    JSON pointers identify evidence rows, not new mathematical results. A
    declared source hash is not presented as a fresh read of that source.
    """
    rows=[]
    for req in bundle['selected_bridge']['current_result_requirements']:
        owner=ref('requirement',req['id'])
        review_hash=pin(req['author_review']['sha256'])
        review=bundle['evidence'][review_hash]
        manifest=bundle['evidence'][pin(req['provider']['reader_manifest']['sha256'])]
        def add(evidence_hash,pointer,target,native,source,role,work,reuse,comparison=None):
            rows.append({'use_locator':{'evidence_sha256':evidence_hash,'json_pointer':pointer},
                'within_record':owner,'target':target,'source_binding':'sha256:'+pin(source['sha256']),
                'source_identity':copy.deepcopy(source),'native_use':copy.deepcopy(native),
                'role':role,'source_work':copy.deepcopy(work),'canonical_source_key':None,
                'reuse_evidence':copy.deepcopy(reuse),'comparison':comparison,
                'source_bytes_checked_by_adapter':False,'accessed_utc':None,
                'consultation_evidence':'Inherited source-use record; no new mathematical source-reading claim',
                'proof_closed_by_adapter':False})
        bindings=[item for item in manifest['files'] if item['path']=='SOURCE_BINDINGS.json']
        need(len(bindings)<=1,'Ambiguous source-binding metadata')
        if bindings:
            binding_hash=pin(bindings[0]['sha256']);binding=bundle['evidence'][binding_hash]
            need(pin(binding['consumer']['source_sha256'])==pin(req['consumer']['source']['sha256']),'Source-use consumer revision conflict')
            for i,fragment in enumerate(binding['source_fragments']):
                relpath(fragment['path']);pin(fragment['sha256'])
                file=binding['source_files'][fragment['path']]
                need(0<=fragment['byte_start']<fragment['byte_end']<=file['bytes'],'Fragment outside bound file')
                need(0<fragment['line_start']<=fragment['line_end'],'Invalid source line range')
                source=dict(file,path=fragment['path'],sha256=pin(file['sha256']),revision=binding['source_revision'])
                work={k:binding[k] for k in ('author','work','source_repository','source_website','source_revision')}
                reuse={k:binding[k] for k in ('selected_license','source_grant_sha256','acknowledgements_sha256','adaptation','source_bytes_modified')}
                add(binding_hash,'/source_fragments/'+str(i),ref('native_result',fragment['result']),fragment,source,
                    'credited_adaptation_'+fragment['role'],work,reuse)
        for i,item in enumerate(review.get('sources_compared',[])):
            source={'sha256':pin(item['sha256'])}
            for key in ('source','source_url','version','archive_sha256'):
                if key in item:source[key]=item[key]
            work={k:item[k] for k in ('author','title','version','programme','source_url') if k in item}
            reuse={k:item[k] for k in ('body_copied','rights_evidence','status') if k in item}
            add(review_hash,'/sources_compared/'+str(i),owner,item,source,'recorded_comparison',work,reuse,item.get('comparison'))
        if review.get('earlier_proof'):
            item=review['earlier_proof'];source={'sha256':pin(item['sha256']),'revision':item['revision']}
            add(review_hash,'/earlier_proof',owner,item,source,'programme_prerequisite_use',
                {'title':item['lesson'],'revision':item['revision']},
                {k:item[k] for k in ('body_copied','rights')},item['use'])
    return rows

def _derive(bundle):
    need(bundle['schema']=='existing-proof-evidence-input/1','Unexpected input schema')
    bridge=bundle['selected_bridge'];requirements=bridge['current_result_requirements']
    reported=bridge['reported_providers'];routes=bridge['source_bound_lesson_routes']
    observations=bundle['observations'];evidence=bundle['evidence']
    identities=set();artifacts={};relationships=[];records=[]
    def artifact(source,role,owner,record_ref):
        h=pin(source.get('sha256',source.get('source_sha256')))
        key='sha256:'+h
        source=copy.deepcopy(source)
        if source.get('path'):relpath(source['path'])
        if source.get('bytes') is not None:need(isinstance(source['bytes'],int) and source['bytes']>0,'Invalid byte count')
        if key not in artifacts:
            artifacts[key]={'binding_id':key,'identity_kind':'content_fingerprint_not_bibliographic_key','sha256':h,'bibliographic_registry_ref':None,'locations':[],'used_by':[]}
        a=artifacts[key];location={'owner':owner,'evidence':source}
        if location not in a['locations']:a['locations'].append(location)
        use={'record':record_ref,'role':role}
        if use not in a['used_by']:a['used_by'].append(use)
        return key
    def add(kind,key,native,**fields):
        ident=(kind,key);need(ident not in identities,'Duplicate existing record identity');identities.add(ident)
        row={'record_kind':kind,'id':key,'global_tag':None,'native_record':copy.deepcopy(native),'native_record_sha256':digest(native),**fields}
        records.append(row);return row
    for requirement in requirements:
        key=requirement['id'];rr=ref('requirement',key)
        need(requirement['required_statement'] and requirement['required_conditions'],'Missing exact required statement/conditions')
        source=requirement['provider']['source'];consumer=requirement['consumer']['source']
        p=artifact(source,'provider_source','core',rr);c=artifact(consumer,'consumer_source_snapshot','core',rr)
        obs=observations.get('requirement:'+key)
        need(obs is not None,'Missing current-revision observation')
        expected=pin(consumer['sha256']);actual=pin(obs['current_consumer']['sha256']) if obs.get('current_consumer') else None
        state='same_bytes' if actual==expected else 'changed_requires_reconciliation' if actual else 'not_located'
        route=evidence.get(requirement['provider']['route']['sha256'].lower())
        review=evidence.get(requirement['author_review']['sha256'].lower())
        need(route is not None and review is not None,'Missing bound route/review metadata')
        need(pin(route['source_sha256'])==pin(source['sha256']),'Route/provider source conflict')
        need(route['content_language']==requirement['provider']['content_language'],'Language disagreement')
        row=add('requirement',key,requirement,
          required_statement=requirement['required_statement'],required_conditions=copy.deepcopy(requirement['required_conditions']),
          provider_binding=p,consumer_binding=c,current_revision_state=state,current_revision_observation=copy.deepcopy(obs),
          provider_scope=copy.deepcopy(requirement['scope']),provider_full_generality=review.get('supplied_generality'),
          content_language=route['content_language'],rights=route['rights'],proof_locators=[{'url':requirement['provider']['reader_url']+'#'+a,'anchor':a,'source_binding':p} for a in requirement['provider']['proof_anchors']],
          source_use_provenance={'route':copy.deepcopy(route),'author_review':copy.deepcopy(review),'access_observed_utc':None,'network_access_check':'not_performed_by_this_adapter','source_reading':'existing author/reviewer evidence retained; no new mathematical reading claim','comparison':'inherited_author_scope_claim_not_new_independent_admission'},
          independent_review=requirement['independent_review'],whole_prerequisite_closure=requirement['whole_prerequisite_closure'],
          current_proof_admission='not_changed_by_adapter')
        for ordinal,use in enumerate(requirement['consumer']['uses']):
            relationships.append({'kind':'requirement_use','requirement':rr,'native_use_index':ordinal,'native_use':copy.deepcopy(use),'provider_binding':p,'consumer_binding':c,'required_conditions':copy.deepcopy(requirement['required_conditions']),'correspondence':'inherited_claim','current_revision_state':state,'proof_closed_by_adapter':False})
    for provider in reported:
        key=provider['id'];rr=ref('reported_provider',key)
        proof=provider['proof'];source={'source_sha256':proof['source_sha256'],'unit':proof['unit'],'anchor':proof['anchor'],'locus':proof['locus']}
        p=artifact(source,'reported_proof_source','advanced',rr)
        obs=observations.get('provider:'+key);need(obs is not None,'Missing provider revision observation')
        actual=pin(obs['current_source']['sha256']) if obs.get('current_source') else None
        expected=pin(proof['source_sha256'])
        state='same_bytes' if actual==expected else 'changed_requires_reconciliation' if actual else 'not_located'
        add('reported_provider',key,provider,title=provider['title'],statement=provider['statement'],conditions=copy.deepcopy(provider['conditions']),proof_locator=copy.deepcopy(proof),source_binding=p,current_revision_state=state,current_revision_observation=copy.deepcopy(obs),contribution_provenance=None,bibliographic_registry_refs=[],content_language=obs.get('content_language'),independent_review=provider['independent_proof_check'],whole_prerequisite_closure=provider['whole_prerequisite_closure'],current_proof_admission='reported_not_newly_admitted')
    for route in routes:
        # Route documents can have many prose-scoped uses. Retain their exact
        # structure; do not invent statement-level correspondences from titles.
        key=route_key(route)
        row=add('lesson_route',key,route,proof_correspondence='native_scoped_evidence_only',global_reading_completion=False)
        for side in ('provider','consumer'):
            source=route.get(side,{})
            if source.get('sha256'):
                artifact(source,side+'_reader',side,ref('lesson_route',key))
    source_use_rows=source_uses(bundle)
    for use in source_use_rows:
        artifact(use['source_identity'],'declared_source_use',use['source_work'].get('programme','source'),use['within_record'])
    source_to_uses={};target_to_uses={}
    for use in source_use_rows:
        source_to_uses.setdefault(use['source_binding'],[]).append(use['use_locator'])
        target_to_uses.setdefault(use['target']['kind'],{}).setdefault(use['target']['id'],[]).append(use['use_locator'])
    lookup={kind:{} for kind in ('requirement','reported_provider','lesson_route')}
    for row in records:lookup[row['record_kind']][row['id']]=[a['binding_id'] for a in artifacts.values() if any(u['record']==ref(row['record_kind'],row['id']) for u in a['used_by'])]
    result={'schema':'existing-proof-evidence-projection/1','scope':'Additive projection of selected existing programme evidence, not a competing source registry',
      'input_identity':{'sha256':digest(bundle),'bridge':bundle['bridge_identity']},
      'records':records,'artifact_bindings':sorted(artifacts.values(),key=lambda x:x['binding_id']),'use_edges':relationships,'record_to_artifacts':lookup,
      'source_uses':source_use_rows,'source_to_uses':source_to_uses,'target_to_uses':target_to_uses,
      'counts':{'requirements':len(requirements),'reported_providers':len(reported),'lesson_routes':len(routes),'explicit_requirement_uses':len(relationships),'source_uses':len(source_use_rows),'artifact_fingerprints':len(artifacts),'new_global_tags':0,'new_mathematical_admissions':0},
      'unknowns':['Canonical bibliography source keys are not fabricated from paths or hashes; existing corpus registry resolves work/version keys.','A missing consultation date or historical AI model remains unknown. Current model identity describes only this adapter.','No course-preparation edge is converted into a proof match.'],
      'production_provenance':{'model':'gpt-6-astra','effort':'ultra','work':'Lossless evidence projection, revision comparison and reference validation','human_review_claimed':False}}
    return result

def project(bundle):
    result=_derive(bundle)
    validate(result,bundle)
    return result

def validate(result,bundle):
    need(result['schema']=='existing-proof-evidence-projection/1','Wrong output schema')
    need(result['input_identity']['sha256']==digest(bundle),'Input binding changed')
    selected=bundle['selected_bridge']
    source={('requirement',r['id']):r for r in selected['current_result_requirements']}
    source.update({('reported_provider',r['id']):r for r in selected['reported_providers']})
    source.update({('lesson_route',route_key(r)):r for r in selected['source_bound_lesson_routes']})
    seen=set();artifacts={a['binding_id']:a for a in result['artifact_bindings']}
    need(len(artifacts)==len(result['artifact_bindings']),'Duplicate artifact identity')
    for a in artifacts.values():
        need(a['binding_id']=='sha256:'+pin(a['sha256']),'Fingerprint disagreement')
        need(a['bibliographic_registry_ref'] is None,'Adapter must not invent bibliography keys')
        need(a['used_by'],'Orphan artifact')
        for u in a['used_by']:need((u['record']['kind'],u['record']['id']) in source,'Dangling reverse reference')
    for row in result['records']:
        identity=(row['record_kind'],row['id']);need(identity in source and identity not in seen,'Unknown/duplicate record');seen.add(identity)
        need(row['native_record']==source[identity] and row['native_record_sha256']==digest(source[identity]),'Native evidence changed')
        need(row['global_tag'] is None,'No independent global tag allocation')
        refs=result['record_to_artifacts'][identity[0]][identity[1]]
        actual=[a['binding_id'] for a in artifacts.values() if any(u['record']==ref(*identity) for u in a['used_by'])]
        need(set(refs)==set(actual),'Forward/reverse index disagreement')
        if identity[0]=='requirement':
            native=source[identity];need(row['required_conditions']==native['required_conditions'] and row['required_statement']==native['required_statement'],'Required scope drift')
            need(row['provider_full_generality']==row['source_use_provenance']['author_review'].get('supplied_generality'),'Provider generality drift')
            need(row['independent_review']==native['independent_review'] and row['whole_prerequisite_closure']==native['whole_prerequisite_closure'],'Review/closure upgrade')
            need(row['content_language']==native['provider']['content_language'],'Language availability invented')
            need(row['source_use_provenance']['access_observed_utc'] is None,'Synthetic network access date')
            need(row['current_proof_admission']=='not_changed_by_adapter','Adapter proof admission forbidden')
            obs=row['current_revision_observation'];old=pin(native['consumer']['source']['sha256']);now=obs.get('current_consumer',{}).get('sha256')
            expected='same_bytes' if now and pin(now)==old else 'changed_requires_reconciliation' if now else 'not_located'
            need(row['current_revision_state']==expected,'Stale consumer silently admitted')
    need(seen==set(source),'Missing input record')
    expected_edges=[(r['id'],i,u) for r in selected['current_result_requirements'] for i,u in enumerate(r['consumer']['uses'])]
    actual_edges=[(e['requirement']['id'],e['native_use_index'],e['native_use']) for e in result['use_edges']]
    need(actual_edges==expected_edges,'Lost, extra or changed use edge')
    for edge in result['use_edges']:
        need(not edge['proof_closed_by_adapter'],'Course or use edge wrongly closes proof')
        need(edge['provider_binding'] in artifacts and edge['consumer_binding'] in artifacts,'Dangling source binding')
    need(result['counts']['new_global_tags']==result['counts']['new_mathematical_admissions']==0,'Invented admission/tag count')
    raw=encoded(result)
    need(not re.search(rb'(?<![A-Za-z])[A-Za-z]:[\\/]',raw),'Private absolute path leaked')
    # This is deterministic serialization/reconciliation, not an independent
    # mathematical audit. Compare ALL derived fields to frozen evidence so a
    # mutable display field cannot drift while its native copy stays intact.
    need(result==_derive(bundle),'Derived field or source-use index differs from frozen evidence')
    return True
