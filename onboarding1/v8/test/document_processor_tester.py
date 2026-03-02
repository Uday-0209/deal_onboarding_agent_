from v8.Backend.document_processor import process_document
from v8.Backend.summary_store import store_document_summary, vectore_store
path = '/Users/workfall/Downloads/GreenEnergy_Solar_Expansion_Deal_Proposal.pdf'
intake = {
"company_name": 'test_company',
"industry": 'test_industry',
"deal_type": 'test_deal',
"geography": 'test_geo'
}
result = process_document('test101', path, intake)
print(result)

# print("\n **************************************\n")
# print("the deal will be stored in the VDB")
# store_document_summary('test_101', result, intake)
# print('\n Document stored as vectore\n')



