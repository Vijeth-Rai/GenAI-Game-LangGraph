import { NextApiRequest, NextApiResponse } from 'next'
import { MongoClient } from 'mongodb'

const MONGODB_URI = "mongodb://172.22.80.1:27017/"

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    const { database, collection } = req.body
    const client = new MongoClient(MONGODB_URI)

    try {
      await client.connect()
      const db = client.db(database)
      const documents = await db.collection(collection).find({}).toArray()
      res.status(200).json(documents)
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch documents' })
    } finally {
      await client.close()
    }
  } else {
    res.status(405).json({ error: 'Method not allowed' })
  }
}